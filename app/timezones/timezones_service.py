from fastapi import HTTPException
from pydantic import BaseModel
import pytz

class TimezoneMap(BaseModel):
  name: str


def get_timezones_list(code: str):
  tzs = pytz.country_timezones.get(code, [])
  # my_timezones = []
  #
  # for tz in tzs:
  #   timezone = pytz.timezone(tz)
  #   timezone_now = datetime.now(timezone)
  #   offset = timezone_now.utcoffset().total_seconds() * 1000  # Offset in milliseconds
  #   my_timezones.append(TimezoneMap(offset=offset, name=tz))

  return [TimezoneMap(name=t) for t in tzs]


def get_country_code(timezone: str):
  for country_code, timezones in pytz.country_timezones.items():
    if timezone in timezones:
      return {'country_code': country_code}

  raise HTTPException(status_code=404, detail='Country code not found')
