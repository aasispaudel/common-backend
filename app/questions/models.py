from pydantic import BaseModel, ConfigDict, UUID4
from app.sql_alchemy.models import correct_option_type


class QuestionModel(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: UUID4 | None = None
  question: str
  option_1: str
  option_2: str
  option_3: str | None = None
  option_4: str | None = None
  option_5: str | None = None
  correct_options: list[correct_option_type]


class EditQuestionModel(BaseModel):
  id: UUID4 | None = None
  question: str | None = None
  option_1: str | None = None
  option_2: str | None = None
  option_3: str | None = None
  option_4: str | None = None
  option_5: str | None = None
  correct_options: list[correct_option_type] | None = None


class AddQuestionResponse(BaseModel):
  question_id: UUID4
  question_count: int
