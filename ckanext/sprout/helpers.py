from ckan import model
import ckan.plugins as p
from ckan.common import c
import ckan.lib.uploader as uploader


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


def resource_max_size():
    max_size_int = uploader.get_max_resource_size()
    return ' Maximum allowed size of the file to upload is {} MB.'.format(str(max_size_int))
