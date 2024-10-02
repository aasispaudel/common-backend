from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from fastapi import HTTPException
from sqlalchemy import select, extract
from sqlalchemy.orm import Session
from datetime import timedelta

from app.exceptions.common_exception import CommonException, ErrorCodes
from app.scheduler.scheduler import scheduler
from app.sql_alchemy.models import Event
from app.events.models import CreateEventRequest, EventsResponse, EventResponse, UpdateEventRequest
from datetime import datetime
from app.email.email_service import send_email, SendEmailType, EmailBody
from pytz import utc

EVENT_PREFIX = 'reminder_'


def add_event(background_tasks, session: Session, event_model: CreateEventRequest):
  try:
    event = Event(**event_model.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)

    # Send confirmation email
    background_tasks.add_task(
      send_email, __make_email_body(event, f'Event {event.title} create successfully'),
      SendEmailType.confirmation
    )

    # Schedule reminder email
    run_date = event.event_from - timedelta(seconds=10)
    if run_date > datetime.now(utc):
      scheduler.add_job(
        send_email,
        'date',
        run_date=run_date,
        args=[__make_email_body(event), SendEmailType.reminder],
        id=f'{EVENT_PREFIX}{event.id}'
      )

    return EventResponse.model_validate(event)
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not save right now. Please try again later')


def get_all_events(session: Session, month: int | None = None, year: int | None = None):
  if month is None:
    month = datetime.now().month
  if year is None:
    year = datetime.now().year

  try:
    events = session.scalars(
      select(Event)
      .where(extract('YEAR', Event.event_from) == year)
      .where(extract('MONTH', Event.event_from) == month)
    ).all()
    return EventsResponse.model_validate({'events': events})
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not retrieve events')


def update_event(background_tasks, event_id: int, session: Session, event_model: UpdateEventRequest):
  try:
    event = session.scalars(select(Event).where(Event.id == event_id)).first()
    if event is None:
      raise CommonException(status_code=404, detail='Event not found', error_code=ErrorCodes.EVENT_NOT_FOUND)

    # Update only those values which are different than db version
    for key, value in event_model.model_dump().items():
      if value is not None:
        if getattr(event, key) != value:
          setattr(event, key, value)

    session.commit()
    session.refresh(event)

    # Schedule modified email with grace
    __modify_job_with_grace(event)
    # Send update confirmation email
    background_tasks.add_task(
      send_email, __make_email_body(event, f'Event {event.title} updated successfully'),
      SendEmailType.update
    )

    return EventResponse.model_validate(event)
  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not update right now. Please try again later')

'''
  Handles different cases of modifying user events
'''
def __modify_job_with_grace(event: Event):
  run_date = event.event_from - timedelta(seconds=10)
  try:
    # Schedule modified email
    job = scheduler.get_job(f'{EVENT_PREFIX}{event.id}')
    if run_date > datetime.now(utc):
      if job is not None and job:
        scheduler.remove_job(f'{EVENT_PREFIX}{event.id}')

      scheduler.add_job(
        send_email,
        'date',
        run_date=run_date,
        args=[__make_email_body(event), SendEmailType.reminder],
        id=f'{EVENT_PREFIX}{event.id}'
        )
    else:
      if job is not None and job:
        scheduler.remove_job(f'{EVENT_PREFIX}{event.id}')
  except JobLookupError as e:
    print('Job not found')
    pass
  except ConflictingIdError as e:
    scheduler.remove_job(f'{EVENT_PREFIX}{event.id}')

def delete_event(background_tasks, event_id: int, session: Session):
  try:
    event = session.scalars(select(Event).where(Event.id == event_id)).first()
    if event is None:
      raise CommonException(status_code=404, detail='Event not found', error_code=ErrorCodes.EVENT_NOT_FOUND)

    session.delete(event)
    session.commit()

    # Remove job
    __remove_job_with_grace(event.id)
    background_tasks.add_task(
      send_email, EmailBody(subject=f'Event {event.title} deleted successfully',
                            participants=event.participants),
      SendEmailType.delete)

    return {'id': event_id}
  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not delete right now. Please try again later')


def __remove_job_with_grace(event_id: int):
  try:
    scheduler.remove_job(f'{EVENT_PREFIX}{event_id}')
  except JobLookupError as e:
    print('Job not found to delete')
    pass


def __make_email_body(event: Event | UpdateEventRequest, subject: str | None = None):
  if subject is None:
    subject = f'Reminder for event: {event.title}'
  return EmailBody(
    subject=subject,
    event_name=event.title,
    event_date=event.event_from.strftime('%Y-%m-%d'),
    event_time=event.event_from.strftime('%H:%M'),
    participants=event.participants
  )
