from typing import Optional

from app.sql_alchemy.models import Base
from app.sql_alchemy.models.commons import CustomBaseUuid, difficulty
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, Uuid


class Quiz(Base, CustomBaseUuid):
  __tablename__ = 'quiz'

  created_at = mapped_column(DateTime, server_default=func.now())
  difficulty: Mapped[difficulty]
  userid = mapped_column(Uuid, nullable=False, server_default=func.auth.uid())
  title: Mapped[str]
  link: Mapped[Optional[str]]
  questions: Mapped[list['Question']] = relationship(back_populates='quiz', order_by='Question.created_at')
