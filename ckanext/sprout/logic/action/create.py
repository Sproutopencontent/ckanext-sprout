from ckan.authz import auth_is_loggedin_user
from ckan import logic
from ckan.plugins import toolkit
from ckan.plugins.toolkit import _

from ckanext.sprout import model as db
from ckanext.sprout.utils import (_dictize_answer_questions,
                                  _get_a_list_of_questions)


def answer_questions(context, data_dict):
    model = context['model']
    session = context['session']
    # Check wether 'resource_id' is provided
    resource_id = logic.get_or_bust(data_dict, 'resource_id')

    # Check if there is a loged in user or Authentication
    if not auth_is_loggedin_user():
        raise logic.NotAuthorized
    user_id = context['auth_user_obj'].id
    user_email = context['auth_user_obj'].email

    # Check if the resource_id is valid( if the resource exists)
    toolkit.get_action('resource_show')(context, {'id': resource_id})

    # Check if the user has already answered the questions for this resource
    has_answered = toolkit.get_action('get_user_and_resource_qa')(
        context, {'user_id': user_id, 'resource_id': resource_id})
    if has_answered:
        raise logic.ValidationError(
            _(f"User '{user_id}' has already answered the questions on resource '{resource_id}'"))

    # Check if the questions submitted are the defined questions
    questions = data_dict['data']
    allowed_questions = _get_a_list_of_questions()
    for question in questions:
        if question['question'] not in allowed_questions:
            raise logic.ValidationError(
                _(f"Question '{question['question']}' is not in defined questions"))
        # TODO:
        # Check if type is select or checkbox whether the answers
        # are compatible with the answers from the config file

    ques_answ = db.Questions()
    ques_answ.user_id = user_id
    ques_answ.resource_id = resource_id
    ques_answ.user_email = user_email
    ques_answ.questions_answers = data_dict['data']
    # Save it to the db
    session.add(ques_answ)
    session.commit()

    # Return the result as a Dict
    resault = _dictize_answer_questions(ques_answ)

    return resault
