from app.quiz.quiz_service import add_quiz
import pytest
from fastapi import HTTPException
from ...conftest import *
import uuid


def test_add_quiz(mocker, mock_session):
  # Fake data
  quiz_request = QuizRequest(difficulty="easy", title="Sample Quiz")
  userid = uuid.uuid4()
  mocked_id = uuid.uuid4()

  # Mocks
  refresh = mocker.patch.object(mock_session, 'refresh')
  refresh.side_effect = lambda obj: setattr(obj, 'id', mocked_id)

  # Call the add_quiz function
  response = add_quiz(mock_session, quiz_request, userid)

  # Assertions
  mock_session.add.assert_called_once()
  mock_session.commit.assert_called_once()
  refresh.assert_called_once()

  assert response.title == quiz_request.title
  assert response.difficulty == quiz_request.difficulty
  assert response.id == mocked_id

def test_add_quiz_exception_on_add(mocker, mock_session):
  # Fake data
  quiz_request = QuizRequest(difficulty="easy", title="Sample Quiz")
  userid = uuid.uuid4()

  # Mock session
  mock_session.add.side_effect = Exception("Database error")

  # Call the add_quiz function and assert exception
  with pytest.raises(HTTPException) as exc_info:
    add_quiz(mock_session, quiz_request, userid)

  # Assertions
  mock_session.add.assert_called_once()
  mock_session.rollback.assert_called_once()
  assert exc_info.value.status_code == 500
  assert exc_info.value.detail == 'Could not save right now. Please try again later'
