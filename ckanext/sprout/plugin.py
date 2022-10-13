import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sprout.sprout_blueprint import blueprint
from ckanext.sprout import helpers as h
from ckanext.pages.interfaces import IPagesSchema
from typing import Any


class SproutPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(IPagesSchema)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IDatasetForm)

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
            'resource_max_size':
                h.resource_max_size,
            'sprout_link_active':
                h.link_active
        }

    # IBlueprint

    def get_blueprint(self):
        return [blueprint]

    # IDatasetForm
    # https://docs.ckan.org/en/2.9/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IDatasetForm

    def package_types(self) -> list[str]:
        return ['forecast']

    def is_fallback(self):
        return False

    def edit_template(self) -> Any:
        # TODO: create a new template that extends a block on the existing template
        # (see https://docs.ckan.org/en/2.9/theming/templates.html#extending-parent-blocks-with-jinja-s-super)
        return super(SproutPlugin, self).edit_template()
