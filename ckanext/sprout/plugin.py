import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sprout.sprout_blueprint import blueprint
from ckanext.sprout.forecaster_blueprint import forecaster_blueprint
from ckanext.sprout import helpers as h
from ckanext.pages.interfaces import IPagesSchema


class SproutPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(IPagesSchema)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IResourceView)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'sprout')

    # IPagesSchema

    def update_pages_schema(self, schema):

        schema.update({
            'featured': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_validator('boolean_validator')]
        })
        return schema

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_featured_pages':
                h.get_featured_pages,
            'resource_display_size':
                h.resource_display_size,
            'resource_download_url':
                h.resource_download_url,
            'resource_max_size':
                h.resource_max_size,
            'sprout_link_active':
                h.link_active
        }

    # IBlueprint

    def get_blueprint(self):
        return [blueprint, forecaster_blueprint]

    # IResourceView
    # This resource view is only used internally by the forecaster

    def info(self):
        return {
            'name': 'forecast_loading_view',
            'title': toolkit._('Forecast Loading'),
            'default_title': toolkit._('Loading')
        }

    def can_view(self, data_dict):
        # TODO: should probably filter on forecast resources too (once we can distinguish them)
        return data_dict['package']['type'] == 'weatherset'

    def setup_template_variables(self, context, data_dict):
        return {}

    def view_template(self, context, data_dict):
        return 'views/forecast_loading_view.html'

    def form_template(self, context, data_dict):
        return 'views/forecast_loading_view_form.html'
