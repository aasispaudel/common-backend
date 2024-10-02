from enum import Enum


class ErrorCodes(Enum):
  ''' Errors for quiz'''
  QUIZ_NOT_FOUND = 'QUIZ_NOT_FOUND'
  NO_QUESTIONS = 'NO_QUESTIONS'

  '''Error codes for questions'''
  MAX_QUESTIONS_REACHED = 'MAX_QUESTIONS_REACHED'
  QUESTION_NOT_FOUND = 'QUESTION_NOT_FOUND'
