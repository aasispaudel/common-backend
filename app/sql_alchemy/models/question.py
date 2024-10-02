from typing import Optional

from app.sql_alchemy.models import Base
from app.sql_alchemy.models.commons import CustomBaseUuid, correct_option_type
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ARRAY, Enum, Uuid, ForeignKey, DateTime, func


class Question(Base, CustomBaseUuid):
  __tablename__ = 'question'

  created_at = mapped_column(DateTime, server_default=func.now())
  question: Mapped[str]
  option_1: Mapped[str]
  option_2: Mapped[Optional[str]]
  option_3: Mapped[Optional[str]]
  option_4: Mapped[Optional[str]]
  option_5: Mapped[Optional[str]]
  correct_options = mapped_column(ARRAY(Enum(correct_option_type)))

  quiz_id = mapped_column(Uuid, ForeignKey('quiz.id'))

  quiz = relationship('Quiz', back_populates='questions')
