from ckan.plugins import toolkit
from ckan.logic import get_or_bust

from ckanext.sprout.utils import _get_qa_of_user_and_resource


@toolkit.side_effect_free
def get_user_and_resource_qa(context, data_dict):
    """Returns the questionnaire data for specified user and resource

    :param user_id: the id of the user
    :type id: string
    "param resource_id: the id of the resource
    :type id: string

    :rtype: dictionary
    """
    user_id = get_or_bust(data_dict, 'user_id')
    resource_id = get_or_bust(data_dict, 'resource_id')

    result = _get_qa_of_user_and_resource(user_id, resource_id)

    return result
