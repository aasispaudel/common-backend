import pytest
from fastapi import HTTPException
from app.quiz.quiz_service import get_single_quiz
from app.quiz.models import QuizResponseWithQuestionCount
from app.sql_alchemy.models import difficulty
from ...conftest import *
from app.exceptions.QuizException import CommonException
import uuid

def test_get_single_quiz_success(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()
    quiz_data = (quiz_id, "Sample Quiz", difficulty.easy, "sample-link", 5)

    # Mock session.execute
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.return_value.first.return_value = quiz_data

    # Call the get_single_quiz function
    response = get_single_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_execute.assert_called_once()
    assert isinstance(response, QuizResponseWithQuestionCount)
    assert response.id == quiz_id
    assert response.title == "Sample Quiz"
    assert response.difficulty == difficulty.easy
    assert response.link == "sample-link"
    assert response.question_count == 5

def test_get_single_quiz_not_found(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.execute to return None
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.return_value.first.return_value = None

    # Call the get_single_quiz function and assert exception
    with pytest.raises(CommonException) as exc_info:
        get_single_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_execute.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Quiz not found'

def test_get_single_quiz_exception(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.execute to raise an exception
    mock_execute = mocker.patch.object(mock_session, 'execute')
    mock_execute.side_effect = Exception("Database error")

    # Call the get_single_quiz function and assert exception
    with pytest.raises(HTTPException) as exc_info:
        get_single_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_execute.assert_called_once()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Could not fetch right now. Please try again later'
