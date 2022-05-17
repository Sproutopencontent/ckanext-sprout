import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.sprout.cli import get_commands
from ckanext.sprout.logic.action import create
from ckanext.sprout.logic.action import get


class SproutPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IClick)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'sprout')

    # IActions
    def get_actions(self):
        return {
            'answer_questions': create.answer_questions,
            'get_user_and_resource_qa': get.get_user_and_resource_qa
        }

    # IClick
    def get_commands(self):
        return get_commands()
