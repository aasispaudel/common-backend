import pytest
from fastapi import HTTPException
from app.questions.question_service import add_question
from app.questions.models import AddQuestionResponse
from app.exceptions.QuizException import CommonException
from ...conftest import *
import uuid

def test_add_question(mock_session, question_only):
  # Define test data
  quiz_id = uuid.uuid4()
  new_question_id = uuid.uuid4()

  # Set up the mock session to return a specific count of questions
  mock_session.scalar.return_value = 5
  mock_session.refresh.side_effect = lambda obj: setattr(obj, 'id', new_question_id)

  # Call the add_question function
  response = add_question(mock_session, question_only, quiz_id)

  # Assert that the function returns the expected result
  assert isinstance(response, AddQuestionResponse)
  assert response.question_count == 6
  assert response.question_id == new_question_id

  # Verify that the session methods are called with the expected arguments
  mock_session.add.assert_called_once()
  mock_session.commit.assert_called_once()
  mock_session.refresh.assert_called_once()


def test_add_question_max_limit_reached(mock_session, question_only):
  # Define test data
  quiz_id = uuid.uuid4()

  # Set up the mock session to return the maximum count of questions
  mock_session.scalar.return_value = 10

  # Call the add_question function and expect a QuizException
  with pytest.raises(CommonException) as exc_info:
    add_question(mock_session, question_only, quiz_id)

  # Assert that the exception has the expected properties
  assert exc_info.value.status_code == 400
  assert exc_info.value.detail == 'Maximum questions limit reached'
  assert exc_info.value.error_code == 'MAX_QUESTIONS_REACHED'

  # Verify that the session methods are not called
  mock_session.add.assert_not_called()
  mock_session.commit.assert_not_called()
  mock_session.refresh.assert_not_called()


def test_add_question_db_error(mock_session, question_only):
  # Define test data
  quiz_id = uuid.uuid4()

  # Set up the mock session to raise an exception
  mock_session.scalar.return_value = 5
  mock_session.commit.side_effect = Exception('Database error')

  # Call the add_question function and expect an HTTPException
  with pytest.raises(HTTPException) as exc_info:
    add_question(mock_session, question_only, quiz_id)

  # Assert that the exception has the expected properties
  assert exc_info.value.status_code == 500
  assert exc_info.value.detail == 'Could not save right now. Please try again later'

  # Verify that the session methods are called with the expected arguments
  mock_session.scalar.assert_called_once()
  mock_session.add.assert_called_once()
  mock_session.commit.assert_called_once()
  mock_session.refresh.assert_not_called()
