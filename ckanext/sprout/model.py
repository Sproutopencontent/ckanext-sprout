# encoding: utf-8
import logging 

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

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
                sa.ForeignKey('resource.id')),
            sa.Column('questions_answers', MutableDict.as_mutable(JSONB))
              )
            
class Questions(domain_object.DomainObject):
    @classmethod
    def get_question_and_anwsers(cls, user_id, resource_id):
        pass


def setup():
    """Create the questions table"""
    questions.create(checkfirst=True)

def drop():
    """Drops the questions table"""
    questions.drop(checkfirst=True)


meta.mapper(Questions, questions)