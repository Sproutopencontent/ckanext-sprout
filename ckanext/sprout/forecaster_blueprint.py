from ckan.common import config
from ckan.plugins import toolkit
import codecs
from datetime import datetime
import flask
import requests
from .forecaster import Forecaster

forecaster_blueprint = flask.Blueprint('forecaster', __name__)

def new_forecast(id):
    dataset = toolkit.get_action('package_show')(None, {'id': id})
    api_key = config.get('ckan.sprout.tomorrow_api_key', None)
    forecaster = Forecaster(api_key=api_key, languages=dataset['language'])
    create_date = datetime.utcnow().isoformat(sep=" ", timespec='minutes')

    # TODO: produce a proper error message if the location_resource can't be found or isn't set
    locations_resource = toolkit.get_action('resource_show')(None, {
        'id': dataset['locations_resource_id']
    })

    # TODO: handle failures here gracefully too
    # Pass along the cookies from this request so we stay authenticated
    locations_response = requests.get(
        locations_resource['url'],
        cookies=toolkit.request.cookies,
        stream=True
    )
    forecasts = forecaster.run(codecs.iterdecode(locations_response.iter_lines(), 'utf-8'))

    # TODO: can we just replace the resource_create action for this package type?
    resource = toolkit.get_action('resource_create')(None, {
        'package_id': id,
        'name': f'{toolkit._("Forecasts")} {create_date}',
        'format': 'csv',
        'language': dataset['language']
    })
    datastore_create = toolkit.get_action('datastore_create')

    for forecast in forecasts:
        datastore_create(None, {
            'resource_id': resource['id'],
            'records': [forecast],
            'force': True
        })

    toolkit.get_action('resource_create_default_resource_views')(None, {
        'resource': resource,
        'package': dataset,
        'create_datastore_views': True
    })

    return toolkit.redirect_to('resource.read', id=id, resource_id=resource["id"])


forecaster_blueprint.add_url_rule('/weatherset/<id>/resource/new_forecast', view_func=new_forecast)
