import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.quiz.quiz_service import update_quiz
from app.quiz.models import UpdateQuizRequest, QuizResponse
from app.sql_alchemy.models import Quiz
from ...conftest import *
from app.exceptions.QuizException import CommonException
from app.exceptions.error_codes import ErrorCodes
import uuid

@pytest.fixture(scope='function')
def update_data():
    q = UpdateQuizRequest(title="New Title", difficulty=difficulty.easy)
    return q

def test_update_quiz_success_update_title(mocker, mock_session, quiz_only, update_data):
    # Mock session.scalars
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = quiz_only

    # Call the update_quiz function
    response = update_quiz(quiz_only.id, update_data, mock_session, quiz_only.userid)

    # Assertions
    mock_scalars.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(quiz_only)
    assert isinstance(response, QuizResponse)
    assert response.title == "New Title"

def test_update_quiz_success_update_difficulty(mocker, mock_session, quiz_only):
    # Fake data
    q = UpdateQuizRequest(title="Sample Quiz", difficulty=difficulty.medium)

    # Mock session.scalars
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = quiz_only

    # Call the update_quiz function
    response = update_quiz(quiz_only.id, q, mock_session, quiz_only.userid)

    # Assertions
    mock_scalars.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(quiz_only)
    assert isinstance(response, QuizResponse)
    assert response.difficulty == difficulty.medium


def test_update_quiz_not_found(mocker, mock_session, update_data):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.scalars to return None
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = None

    # Call the update_quiz function and assert exception
    with pytest.raises(CommonException) as exc_info:
        update_quiz(quiz_id, update_data, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Quiz not found'

def test_update_quiz_exception(mocker, mock_session, update_data):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.scalars to raise an exception
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.side_effect = Exception("Database error")

    # Call the update_quiz function and assert exception
    with pytest.raises(HTTPException) as exc_info:
        update_quiz(quiz_id, update_data, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Could not fetch right now. Please try again later'
