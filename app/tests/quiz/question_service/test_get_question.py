import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.questions.question_service import get_question
from app.questions.models import QuestionModel
from ...conftest import *
import uuid

def test_get_question(mock_session, question_only):
    # Define test data
    question_id = question_only.id

    # Set up the mock session to return a specific question
    mock_session.scalars.return_value.first.return_value = question_only

    # Call the get_question function
    response = get_question(question_id, mock_session)

    # Assertions
    assert isinstance(response, QuestionModel)
    assert response.question == question_only.question
    assert response.id == question_id
    assert response.option_1 == question_only.option_1

    mock_session.scalars.assert_called_once()

def test_get_question_not_found(mock_session):
    # Define test data
    question_id = uuid.uuid4()

    # Set up the mock session to return None
    mock_session.scalars.return_value.first.return_value = None

    # Call the get_question function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_question(question_id, mock_session)

    # Assert that the exception has the expected properties
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Question does not exist'

    # Verify that the session methods are called with the expected arguments
    mock_session.scalars.assert_called_once()

def test_get_question_db_error(mock_session):
    # Define test data
    question_id = uuid.uuid4()

    # Set up the mock session to raise an exception
    mock_session.scalars.side_effect = Exception('Database error')

    # Call the get_question function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_question(question_id, mock_session)

    # Assert that the exception has the expected properties
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Question could not be loaded. Try later.'

    # Verify that the session methods are called with the expected arguments
    mock_session.scalars.assert_called_once()
