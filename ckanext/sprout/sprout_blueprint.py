from ckan.views.resource import download as download_resource
from ckan.common import g
import ckan.lib.helpers as h
import flask

blueprint = flask.Blueprint(
    u'sprout_blueprint',
    __name__,
    url_prefix=u'/dataset/<id>/resource',
    url_defaults={u'package_type': u'dataset'}
)


def download_to(package_type, id, resource_id, filename=None):
    """
    Provides a direct download by either redirecting the user to the url
    stored or downloading an uploaded file directly.
    """
    if not g.user:
        came_from = h.current_url()
        came_from = came_from.split('/download')[0]
        return h.redirect_to(u'user.login', came_from=came_from)
    else:
        return download_resource(package_type, id, resource_id, filename=filename)


blueprint.add_url_rule(u'/<resource_id>/download', view_func=download_to)
blueprint.add_url_rule(u'/<resource_id>/download/<filename>', view_func=download_to)
