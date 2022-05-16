# encoding: utf-8
import logging
import datetime

import sqlalchemy as sa

from ckan import model
from ckan.model import meta
from ckan.model import types as _types
from ckan.model import domain_object


log = logging.getLogger(__name__)


__all__ = ['Questions', 'questions']


questions = sa.Table('questions', meta.metadata,
                     sa.Column('id', sa.types.UnicodeText, primary_key=True,
                               default=_types.make_uuid),
                     sa.Column('user_id', sa.types.UnicodeText,
                               nullable=False),
                     sa.Column('resource_id', sa.types.UnicodeText,
                               nullable=False),
                     sa.Column('questions_answers', _types.JsonDictType),
                     sa.Column('created', sa.types.DateTime,
                               default=datetime.datetime.now))


class Questions(domain_object.DomainObject):
    @classmethod
    def get_question_and_anwser(cls, user_id, resource_id):
        query = model.Session.query(cls).\
            filter_by(user_id=user_id, resource_id=resource_id).first()
        return query


def setup():
    """Create the questions table"""
    questions.create(checkfirst=True)


def drop():
    """Drops the questions table"""
    questions.drop(checkfirst=True)


meta.mapper(Questions, questions)
