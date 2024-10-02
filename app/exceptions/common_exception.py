from fastapi import HTTPException
from .error_codes import ErrorCodes


class CommonException(HTTPException):

  """HTTP Exception alternative for concise error handling while throwing different errors
  from inside try block"""
  def __init__(self, status_code: int, detail: str, error_code: ErrorCodes):
    self.status_code = status_code
    self.detail = detail
    self.error_code = error_code.value
    super().__init__(self.status_code, self.detail)

  def __str__(self):
    return f'{self.status_code}: {self.detail}'
