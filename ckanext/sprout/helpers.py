from ckan import model
import ckan.plugins as p
from ckan.common import c


def get_featured_pages(limit=3):
    data_dict = {'org_id': None, 'page_type': 'page'}
    context = {'model': model, 'user': c.user,
               'auth_user_obj': c.userobj}
    pages = p.toolkit.get_action('ckanext_pages_list')(context, data_dict)[:limit]
    return pages
