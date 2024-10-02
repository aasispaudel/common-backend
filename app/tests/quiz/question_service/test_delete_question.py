import pytest
from fastapi import HTTPException
from app.questions.question_service import delete_question
from app.exceptions.QuizException import CommonException
from ...conftest import *
from app.exceptions.error_codes import ErrorCodes
import uuid

def test_delete_question(mock_session, question_only):
    # Define test data
    question_id = question_only.id
    user_id = uuid.uuid4()

    # Set up the mock session to return a specific question
    mock_session.scalars.return_value.first.return_value = question_only

    # Call the delete_question function
    response = delete_question(question_id, mock_session, user_id)

    # Assertions
    assert response == {'id': question_only.id}

    mock_session.scalars.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.delete.assert_called_once_with(question_only)

def test_delete_question_not_found(mock_session):
    # Define test data
    question_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Set up the mock session to return None
    mock_session.scalars.return_value.first.return_value = None

    # Call the delete_question function and expect a QuizException
    with pytest.raises(CommonException) as exc_info:
        delete_question(question_id, mock_session, user_id)

    # Assert that the exception has the expected properties
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Question does not exist.'
    assert exc_info.value.error_code == 'QUESTION_NOT_FOUND'

    # Verify that the session methods are called with the expected arguments
    mock_session.scalars.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.delete.assert_not_called()

def test_delete_question_db_error(mock_session, question_only):
    # Define test data
    question_id = question_only.id
    user_id = uuid.uuid4()

    # Set up the mock session to return a specific question
    mock_session.scalars.return_value.first.return_value = question_only
    mock_session.commit.side_effect = Exception('Database error')

    # Call the delete_question function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete_question(question_id, mock_session, user_id)

    # Assert that the exception has the expected properties
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Could not delete questions. Try later.'

    # Verify that the session methods are called with the expected arguments
    mock_session.scalars.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.delete.assert_called_once_with(question_only)
