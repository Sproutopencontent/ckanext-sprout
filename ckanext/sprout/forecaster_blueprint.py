import ckan.lib.helpers as h
from ckan.plugins import toolkit
import codecs
from datetime import datetime, timedelta
import flask
import logging
import requests
from .forecaster import Forecaster

forecaster_blueprint = flask.Blueprint('forecaster', __name__)

def _get_most_recent_forecast(dataset):
    most_recent_forecast = None

    for res in dataset['resources']:
        if 'type' not in res or res['type'] != 'FORECAST':
            continue
        elif most_recent_forecast is None:
            most_recent_forecast = res
        else:
            created_at = h.date_str_to_datetime(res['created'])
            most_recent_created_at = h.date_str_to_datetime(most_recent_forecast['created'])
            if created_at > most_recent_created_at:
                most_recent_forecast = res

    return most_recent_forecast

def _update_forecast_status(context, resource_id, new_status):
    # This is essentially a re-implementation of resource_patch since resource_patch does not
    # support the ignore_auth context parameter.
    resource = toolkit.get_action('resource_show')(context.copy(), {'id': resource_id})
    resource['forecast_status'] = new_status
    toolkit.get_action('resource_update')(context.copy(), resource)

def new_forecast(id):
    dataset = toolkit.get_action('package_show')(None, {'id': id})
    forecast_lifetime_h = toolkit.asint(toolkit.config.get('ckan.sprout.forecast_lifetime_in_hours', 0))
    # CKAN's internal timestamps are always UTC, so that's what we need here for comparison
    now = datetime.utcnow()
    most_recent_forecast = _get_most_recent_forecast(dataset)

    # Look to see if the most recent forecast is still "live" (based on the lifetime config value).
    # If one already exists, just redirect there.
    if most_recent_forecast is not None:
        most_recent_created_at = h.date_str_to_datetime(most_recent_forecast['created'])
        if now - most_recent_created_at < timedelta(hours=forecast_lifetime_h):
            h.flash_notice(toolkit._('Showing you the latest forecast, which is still fresh.'))
            return toolkit.redirect_to(
                'weatherset_resource.read',
                id=id,
                resource_id=most_recent_forecast['id']
            )

    if 'locations_resource_id' not in dataset or not dataset['locations_resource_id']:
        h.flash_error(toolkit._('Please set locations_resource_id before generating a forecast'))
        return toolkit.redirect_to('weatherset.read', id=id)

    # Before we start the background job, make sure the user has access to update this package.
    # check_access will throw an exception if they don't.
    toolkit.check_access('package_update', {}, {'id': id})

    resource = toolkit.get_action('resource_create')(None, {
        'package_id': dataset['id'],
        'name': f'{toolkit._("Forecasts")} {h.render_datetime(now, with_hours=True)}',
        'format': 'csv',
        'language': dataset['language'],
        'type': 'FORECAST',
        # Forecasts start out in progress, the background task will mark them complete or partial
        'forecast_status': 'IN_PROGRESS'
    })

    toolkit.enqueue_job(
        forecaster_job,
        # Pass along the cookies from this request so we stay authenticated
        [dataset, resource, toolkit.request.cookies],
        title='forecaster',
        rq_kwargs={'timeout': 1800}
    )
    return toolkit.redirect_to('weatherset_resource.read', id=id, resource_id=resource['id'])

def forecaster_job(dataset, resource, cookies):
    log = logging.getLogger(__name__)
    log.info('Forecaster starting')

    # This seems to be the only way to get the actions to work in a background job
    from ckan import model
    context = {
        'model': model,
        'session': model.Session,
        'ignore_auth': True,
        'user': '',
    }

    try:
        api_key = toolkit.config.get('ckan.sprout.tomorrow_api_key', None)
        # TODO: this doesn't seem to be returning the same thing the helper function uses
        tz = h.get_display_timezone()
        forecaster = Forecaster(api_key=api_key, languages=dataset['language'], timezone=tz)
        # TODO: produce a user-visible error message if the location_resource can't be found
        # We have to pass a copy of the context dictionary because the action may modify it
        locations_resource = toolkit.get_action('resource_show')(context.copy(), {
            'id': dataset['locations_resource_id']
        })

        # Pass along the provided cookies so we stay authenticated
        locations_response = requests.get(
            locations_resource['url'],
            cookies=cookies,
            stream=True
        )

        forecasts = forecaster.run(codecs.iterdecode(locations_response.iter_lines(), 'utf-8'))

        for forecast in forecasts:
            # Add one row at a time so we don't have to store everything in memory
            # We have to pass a copy of the context dictionary because the action may modify it
            toolkit.get_action('datastore_create')(context.copy(), {
                'resource_id': resource['id'],
                'records': [forecast],
                'force': True
            })

        _update_forecast_status(context, resource['id'], 'COMPLETE')
        log.info(f'Forecasts complete for dataset {dataset["id"]} resource {resource["id"]}')
    except Exception:
        log.exception('Unexpected error')
        _update_forecast_status(context, resource['id'], 'PARTIAL')
        raise



forecaster_blueprint.add_url_rule('/weatherset/<id>/resource/new_forecast', view_func=new_forecast)
