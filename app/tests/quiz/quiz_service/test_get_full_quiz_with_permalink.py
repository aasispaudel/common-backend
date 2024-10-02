import pytest
from fastapi import HTTPException
from app.quiz.quiz_service import get_full_quiz_with_permalink
from app.quiz.models import FullQuizResponse
from ...conftest import *
from app.exceptions.QuizException import CommonException

def test_get_full_quiz_with_permalink_success(mocker, mock_session, full_quiz):
    # Fake data
    permalink = "a1b2c3"
    full_quiz.link = permalink

    # Mock session.execute
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.return_value.first.return_value = (full_quiz,)

    # Call the get_full_quiz_with_permalink function
    response = get_full_quiz_with_permalink(permalink, mock_session)

    # Assertions
    mock_execute.assert_called_once()
    assert isinstance(response, FullQuizResponse)
    assert response.title == full_quiz.title
    assert response.difficulty == full_quiz.difficulty
    assert response.link == permalink
    assert len(response.questions) == 2

def test_get_full_quiz_with_permalink_not_found(mocker, mock_session):
    # Fake data
    permalink = "a1b2c3"

    # Mock session.execute to return None
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.return_value.first.return_value = None

    # Call the get_full_quiz_with_permalink function and assert exception
    with pytest.raises(CommonException) as exc_info:
        get_full_quiz_with_permalink(permalink, mock_session)

    # Assertions
    mock_execute.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Quiz not found'

def test_get_full_quiz_with_permalink_exception(mocker, mock_session):
    # Fake data
    permalink = "sample-permalink"

    # Mock session.execute to raise an exception
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.side_effect = Exception("Database error")

    # Call the get_full_quiz_with_permalink function and assert exception
    with pytest.raises(HTTPException) as exc_info:
        get_full_quiz_with_permalink(permalink, mock_session)

    # Assertions
    mock_execute.assert_called_once()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Could not fetch right now. Please try again later'
