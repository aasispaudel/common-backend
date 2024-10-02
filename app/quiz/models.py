from uuid import UUID

from pydantic import BaseModel, UUID4, ConfigDict

from app.questions.models import QuestionModel
from app.sql_alchemy.models.commons import difficulty as Difficulty, correct_option_type


class QuizRequest(BaseModel):
  title: str
  difficulty: Difficulty

class UpdateQuizRequest(BaseModel):
  title: str | None = None
  difficulty: Difficulty | None = None

class QuizResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: UUID4
  title: str
  difficulty: Difficulty
  link: str | None = None


class QuizResponseWithQuestionCount(QuizResponse):
  question_count: int


class QuizzesResponse(BaseModel):
  next: str | None
  quizzes: list[QuizResponse]


class FullQuizResponse(QuizResponse):
  model_config = ConfigDict(from_attributes=True)

  questions: list[QuestionModel]
