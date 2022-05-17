from typing import List, Dict, Type, Optional

from ckan import logic
from ckan.plugins.toolkit import _, config

from ckanext.sprout import model
from ckanext.sprout.model import Questions


# List of allowed question types
ALLOWED_QUESTION_TYPES = [
    'input',
    'select',
    'checkbox'
]


def _dictize_answer_questions(data: Questions) -> dict:
    if not data:
        return None
    # Convert datetime to String so it can be JSON serializable
    created = str(data.created)
    data_dict = {
        'id': data.id,
        'user_id': data.user_id,
        'resource_id': data.resource_id,
        'questions_answers': data.questions_answers,
        'created': created
    }
    return data_dict


def _get_questions_and_types() -> List[Dict[str, str]]:
    questions = config.get('sprout.questions', None)
    list_of_questions = questions.split(';')
    if list_of_questions[-1] == "":
        list_of_questions.pop()
    ques_and_types = []
    for _question in list_of_questions:
        # Get the question and the type of question
        question_and_type = _question.split('#')
        question = question_and_type[0]
        ques_type = question_and_type[1]
        # Check for unallowed types
        if ques_type not in ALLOWED_QUESTION_TYPES:
            raise logic.ValidationError(_(
                f"Question type \"{ques_type}\" not allowed"))
        res_dict = {"question": question, "type": ques_type}
        ques_and_types.append(res_dict)

    return ques_and_types


def _get_a_list_of_questions() -> list:
    """Returns a list of questions"""
    ques_and_types = _get_questions_and_types()
    list_of_questions = []
    for question in ques_and_types:
        list_of_questions.append(question['question'])

    return list_of_questions


def _get_qa_of_user_and_resource(user_id, resource_id) -> Optional[Dict]:
    """Returns a dict of the data of the questionnaire
    for a user and resource, or returns None
    """
    result = model.Questions.get_question_and_anwser(user_id, resource_id)
    res_dict = _dictize_answer_questions(result)

    return res_dict
