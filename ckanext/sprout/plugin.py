import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.sprout import helpers as h

from ckanext.pages.interfaces import IPagesSchema


class SproutPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(IPagesSchema)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'sprout')

    # IPagesSchema

    def update_pages_schema(self, schema):
        schema.update({
            'featured': [
                toolkit.get_validator('not_empty'),
                toolkit.get_validator('boolean_validator')]
        })
        return schema

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_featured_pages':
                h.get_featured_pages
        }
