from ckan.plugins import toolkit
from ckan.views.resource import download
from datetime import datetime
import flask
import os
from .forecaster import Forecaster

forecaster_blueprint = flask.Blueprint('forecaster', __name__)

def new_forecast(id):
    dataset = toolkit.get_action('package_show')(None, {'id': id})
    # TODO: probably the api key should be in the CKAN config
    forecaster = Forecaster(os.environ.get('TOMORROW_API_KEY'), languages=dataset['languages'])
    create_date = datetime.utcnow().isoformat(sep=" ", timespec='minutes')

    # TODO: store the locations as a resource and load them here
    forecasts = forecaster.run(['latitude,longitude', '-0.344979,36.530516', '-0.27243,36.374660'])

    # TODO: can we just replace the resource_create action for this package type?
    resource = toolkit.get_action('resource_create')(None, {
        'package_id': id,
        'name': create_date
    })

    for forecast in forecasts:
        toolkit.get_action('datastore_create')(None, {
            'resource_id': resource['id'],
            'records': [forecast]
        })

    return toolkit.redirect_to(f'/forecast/{id}/resource/{resource["id"]}')


forecaster_blueprint.add_url_rule('/forecast/<id>/new', view_func=new_forecast)
