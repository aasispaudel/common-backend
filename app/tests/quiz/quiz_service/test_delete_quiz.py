import pytest
from fastapi import HTTPException
from app.quiz.quiz_service import delete_quiz
from app.exceptions.QuizException import CommonException
from ...conftest import *
import uuid

def test_delete_quiz_success(mocker, mock_session, quiz_only):
    # Mock session.scalars
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = quiz_only

    # Call the delete_quiz function
    response = delete_quiz(quiz_only.id, mock_session, quiz_only.userid)

    # Assertions
    mock_scalars.assert_called_once()
    mock_session.delete.assert_called_once_with(quiz_only)
    mock_session.commit.assert_called_once()
    assert response == {'id': quiz_only.id}

def test_delete_quiz_not_found(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.scalars to return None
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.first.return_value = None

    # Call the delete_quiz function and assert exception
    with pytest.raises(CommonException) as exc_info:
        delete_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Quiz does not exist."

def test_delete_quiz_exception(mocker, mock_session):
    # Fake data
    quiz_id = uuid.uuid4()
    userid = uuid.uuid4()

    # Mock session.scalars to raise an exception
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.side_effect = Exception("Database error")

    # Call the delete_quiz function and assert exception
    with pytest.raises(HTTPException) as exc_info:
        delete_quiz(quiz_id, mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Could not delete quiz. Try later.'
