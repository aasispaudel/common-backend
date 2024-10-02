from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

from app.sql_alchemy.models.commons import *
from app.sql_alchemy.models.quiz import Quiz
from app.sql_alchemy.models.question import Question
from app.sql_alchemy.models.events import *
