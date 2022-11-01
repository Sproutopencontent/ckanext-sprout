from ckan.common import config
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
        if 'locations_resource_id' in dataset and res['id'] == dataset['locations_resource_id']:
            # TODO: it would be nice to have some explicit field indicating this is a forecast
            # Right now we're just skipping the locations resource and considering everything else
            continue
        elif most_recent_forecast is None:
            most_recent_forecast = res
        else:
            created_at = h.date_str_to_datetime(res['created'])
            most_recent_created_at = h.date_str_to_datetime(most_recent_forecast['created'])
            if created_at > most_recent_created_at:
                most_recent_forecast = res

    return most_recent_forecast

def new_forecast(id):
    dataset = toolkit.get_action('package_show')(None, {'id': id})
    forecast_lifetime_h = toolkit.asint(config.get('ckan.sprout.forecast_lifetime_in_hours', 0))
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

    resource = toolkit.get_action('resource_create')(None, {
        'package_id': dataset['id'],
        'name': f'{toolkit._("Forecasts")} {h.render_datetime(now, with_hours=True)}',
        'format': 'csv',
        'language': dataset['language']
    })

    toolkit.enqueue_job(
        forecaster_job,
        # Pass along the cookies from this request so we stay authenticated
        [dataset, resource, toolkit.request.cookies],
        title='forecaster',
        rq_kwargs={'timeout': 1200}
    )
    return toolkit.redirect_to('weatherset_resource.read', id=id, resource_id=resource["id"])

def forecaster_job(dataset, resource, cookies):
    logging.info('Forecaster starting')
    try:
        api_key = config.get('ckan.sprout.tomorrow_api_key', None)
        # TODO: this doesn't seem to be returning the same thing the helper function uses
        tz = h.get_display_timezone()
        forecaster = Forecaster(api_key=api_key, languages=dataset['language'], timezone=tz)
        # TODO: produce a user-visible error message if the location_resource can't be found
        locations_resource = toolkit.get_action('resource_show')(None, {
            'id': dataset['locations_resource_id']
        })

        # Pass along the provided cookies so we stay authenticated
        locations_response = requests.get(
            locations_resource['url'],
            cookies=cookies,
            stream=True
        )

        forecasts = forecaster.run(codecs.iterdecode(locations_response.iter_lines(), 'utf-8'))

        datastore_create = toolkit.get_action('datastore_create')

        for forecast in forecasts:
            # Add one row at a time so we don't have to store everything in memory
            datastore_create(None, {
                'resource_id': resource['id'],
                'records': [forecast],
                'force': True
            })

        # Add the resource views (like the data preview), they don't get added to empty resources on
        # creation
        toolkit.get_action('resource_create_default_resource_views')(None, {
            'resource': resource,
            'package': dataset,
            'create_datastore_views': True
        })

        logging.info(f'Forecasts complete for dataset {dataset["id"]} resource {resource["id"]}')
    except requests.exceptions.RequestException:
        logging.exception('Could not fetch locations resource')
    except Exception:
        logging.exception('Unexpected error')



forecaster_blueprint.add_url_rule('/weatherset/<id>/resource/new_forecast', view_func=new_forecast)
