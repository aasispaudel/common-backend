import pytest
from fastapi import HTTPException
from app.quiz.quiz_service import publish_quiz
from app.quiz.models import QuizResponse
from app.sql_alchemy.models import Quiz
from app.exceptions.QuizException import CommonException
from ...conftest import *
from app.exceptions.error_codes import ErrorCodes
import uuid

def test_publish_quiz_success(mocker, mock_session, full_quiz):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()
    full_quiz.id = quiz_id
    full_quiz.userid = userid

    # Mock session.scalars
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = full_quiz
    mock_scalars.refresh = lambda obj: setattr(obj, 'link', "a1b2c3")

    # Mock generate_unique_permalink
    mock_generate_permalink = mocker.patch('app.quiz.quiz_service.generate_unique_permalink')
    mock_generate_permalink.return_value = "a1b2c3"

    # Call the publish_quiz function
    response = publish_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    mock_generate_permalink.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(full_quiz)
    assert isinstance(response, QuizResponse)
    assert response.link == "a1b2c3"

def test_publish_quiz_not_found(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.scalars to return None
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = None

    # Call the publish_quiz function and assert exception
    with pytest.raises(CommonException) as exc_info:
        publish_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Quiz not found'

def test_publish_quiz_no_questions(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()
    quiz_data = Quiz(id=quiz_id, title="Sample Quiz", difficulty="easy", userid=userid, link=None, questions=[])

    # Mock session.scalars
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = quiz_data

    # Call the publish_quiz function and assert exception
    with pytest.raises(CommonException) as exc_info:
        publish_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == 'Cannot publish quiz without any questions'

def test_publish_quiz_exception(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.scalars to raise an exception
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.side_effect = Exception("Database error")

    # Call the publish_quiz function and assert exception
    with pytest.raises(HTTPException) as exc_info:
        publish_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Could not publish right now. Please try again later'