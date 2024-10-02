from functools import wraps
from fastapi import HTTPException

from app.exceptions.common_exception import CommonException


def error_handler(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except CommonException as e:
      raise e
    except Exception as e:
      raise HTTPException(status_code=500, detail=f'Error: {e}')

  return wrapper
