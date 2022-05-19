from flask import Blueprint
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.uploader as uploader
import ckan.model as model
from ckan.common import _, g, request
import ckan.lib.helpers as h
import ckan.views.user as user
import ckan.plugins.toolkit as toolkit
from ckan.views.resource import download

blueprint = Blueprint(
    u'sprout_blueprint',
    __name__,
    url_prefix=u'/dataset/<id>/resource',
    url_defaults={u'package_type': u'dataset'}
)

@blueprint.before_request
def before_request():
    pass


def download_to(package_type, id, resource_id, filename=None):
    """
    Provides a direct download by either redirecting the user to the url
    stored or downloading an uploaded file directly.
    """

    if g.user:
        return h.redirect_to(u'resource.download', package_type=package_type,
                             id=id, resource_id=resource_id, filename=filename)
    else:
        came_from = h.current_url()
        came_from = came_from.split('/download')[0]
        return h.redirect_to(u'user.login', came_from=came_from)

blueprint.add_url_rule(u'/<resource_id>/download', view_func=download_to)
blueprint.add_url_rule(u'/<resource_id>/download/<filename>', view_func=download_to)
