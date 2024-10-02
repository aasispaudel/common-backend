from pydantic import BaseModel, ConfigDict, root_validator, model_validator
from datetime import datetime

class CreateEventRequest(BaseModel):
  title: str
  description: str | None = None
  event_from: datetime
  event_to: datetime
  participants: list[str] = []

  @model_validator(mode='after')
  def check_dates(self):
    if self.event_from is not None and self.event_to is not None and self.event_from > self.event_to:
      raise ValueError('from_date must be less than to_date')
    return self

class UpdateEventRequest(BaseModel):
  id: int | None = None
  title: str | None = None
  description: str | None = None
  event_from: datetime | None = None
  event_to: datetime | None = None
  participants: list[str] | None = None

  @model_validator(mode='after')
  def check_dates(self):
    if self.event_from is not None and self.event_to is not None and self.event_from > self.event_to:
      raise ValueError('from_date must be less than to_date')
    return self


class EventResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  title: str
  description: str | None = None
  event_from: datetime
  event_to: datetime
  participants: list[str] = []


class EventsResponse(BaseModel):
  events: list[EventResponse]
