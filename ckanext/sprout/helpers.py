from ckan import model
import ckan.plugins as p
from ckan.common import c
import ckan.lib.uploader as uploader
from ckan.lib.helpers import _link_active, is_url, url_for


def get_featured_pages(limit=3):
    data_dict = {'org_id': None, 'page_type': 'blog'}
    context = {'model': model, 'user': c.user,
               'auth_user_obj': c.userobj}
    pages = p.toolkit.get_action('ckanext_pages_list')(context, data_dict)
    featured = [page for page in pages if page['featured']]
    return featured[:limit]


def resource_display_size(resource_dict_size):
    resource_size = resource_dict_size.get('size', None)
    resource_size_string = '0' if resource_size is None else '{}'.format(resource_size)
    return resource_size_string


def resource_download_url(res):
    if 'url' in res and is_url(res['url']):
        return res['url']
    if res.get('datastore_active', False):
        return url_for('datastore.dump', resource_id=res['id'], bom=True)
    return None


def resource_max_size():
    return uploader.get_max_resource_size()


def link_active(controller, action):
    if _link_active(dict(controller=controller, action=action)):
        return 'active'


