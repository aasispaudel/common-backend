import pytest
from fastapi import HTTPException
from app.quiz.quiz_service import get_full_quiz_with_id
from app.quiz.models import FullQuizResponse
from ...conftest import *
from app.exceptions.QuizException import CommonException

def test_get_full_quiz_with_id_success(mocker, mock_session, full_quiz):
    # Fake data
    permalink = "a1b2c3"
    full_quiz.link = permalink

    # Mock session.execute
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.return_value.first.return_value = (full_quiz,)

    # Call the get_full_quiz_with_id function
    response = get_full_quiz_with_id(full_quiz.id, mock_session, full_quiz.userid)

    # Assertions
    mock_execute.assert_called_once()
    assert isinstance(response, FullQuizResponse)
    assert response.id == full_quiz.id
    assert response.title == full_quiz.title
    assert response.difficulty == full_quiz.difficulty
    assert response.link == permalink
    assert len(response.questions) == 2

def test_get_full_quiz_with_id_not_found(mocker, mock_session, full_quiz):
    # Mock session.execute to return None
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.return_value.first.return_value = None

    # Call the get_full_quiz_with_id function and assert exception
    with pytest.raises(CommonException) as exc_info:
        get_full_quiz_with_id(full_quiz.id, mock_session, full_quiz.userid)

    # Assertions
    mock_execute.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Quiz not found'

def test_get_full_quiz_with_id_exception(mocker, mock_session, full_quiz):
    # Mock session.execute to raise an exception
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.side_effect = Exception("Database error")

    # Call the get_full_quiz_with_id function and assert exception
    with pytest.raises(HTTPException) as exc_info:
        get_full_quiz_with_id(full_quiz.id, mock_session, full_quiz.userid)

    # Assertions
    mock_execute.assert_called_once()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Could not fetch right now. Please try again later'
