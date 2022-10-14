import ckan.plugins.toolkit as toolkit
from datetime import datetime
import flask

forecaster = flask.Blueprint('forecaster', __name__)

def new_forecast(id):
    create_date = datetime.utcnow().isoformat(sep=" ")
    resource = toolkit.get_action('resource_create')(
        package_id=id,
        # TODO: actual content!
        url='https://cs-tf.com/wp-content/uploads/2021/08/Frizzle-chicken.webp',
        # TODO: localize the name
        name=f'Forecast generated at {create_date}',
        format='csv'
    )
    return toolkit.redirect_to(resource["url"])


forecaster.add_url_rule('/forecast/<id>/new', view_func=new_forecast)
