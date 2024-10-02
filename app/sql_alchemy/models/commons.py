from enum import Enum

from sqlalchemy import Uuid, func
from sqlalchemy.orm import mapped_column


class correct_option_type(Enum):
  A = "A"
  B = "B"
  C = "C"
  D = "D"
  E = "E"

class difficulty(Enum):
  easy = "easy"
  medium = "medium"
  hard = "hard"

class CommonReprMixin:
  def __repr__(self):
    class_name = self.__class__.__name__
    attributes = ', '.join(f"{attr}={getattr(self, attr)!r}" for attr in self.__dict__.keys())
    return f"{class_name}({attributes})"


class CustomBaseUuid(CommonReprMixin):
  id = mapped_column(Uuid, primary_key=True, server_default=func.gen_random_uuid())
