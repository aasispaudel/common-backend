from unittest.mock import call, ANY

import pytest
from fastapi import HTTPException

from app.questions import question_service
from app.questions.question_service import update_question
from app.questions.models import EditQuestionModel, QuestionModel
from app.exceptions.QuizException import CommonException
from ...conftest import *
from app.exceptions.error_codes import ErrorCodes
import uuid

@pytest.fixture(scope='function')
def edit_question_model():
    edit_question_model = EditQuestionModel(
        question="Updated question?",
        option_1="Updated option 1",
        option_2="Updated option 2",
        option_3="Updated option 3",
        option_4="Updated option 4",
        option_5="Updated option 5",
        correct_options=['A', 'B']
    )
    return edit_question_model

def test_update_question(mock_session, question_only, edit_question_model):
    # Define test data
    question_id = question_only.id
    user_id = uuid.uuid4()

    # Set up the mock session to return a specific question
    mock_session.scalars.return_value.first.return_value = question_only

    # Call the update_question function
    response = update_question(edit_question_model, question_id, mock_session, user_id)

    # Assertions
    assert isinstance(response, QuestionModel)
    assert response.id == question_only.id
    assert response.question == edit_question_model.question
    assert response.option_1 == edit_question_model.option_1
    assert response.correct_options == edit_question_model.correct_options

    mock_session.scalars.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_update_question_partial_1(mocker, mock_session, question_only):
    # Define test data
    question_id = question_only.id
    user_id = uuid.uuid4()
    edit_question_model = EditQuestionModel(
        question=question_only.question,
        option_1="Updated option 1",
        option_2="Updated option 2",
        option_3=question_only.option_3,
        option_4=question_only.option_4,
        option_5=question_only.option_5,
        correct_options=question_only.correct_options
    )

    # Set up the mock session to return a specific question
    mock_session.scalars.return_value.first.return_value = question_only

    # Call the update_question function
    response = update_question(edit_question_model, question_id, mock_session, user_id)

    # Assertions
    assert isinstance(response, QuestionModel)
    assert response.id == question_only.id
    assert response.question == question_only.question
    assert response.option_1 == edit_question_model.option_1
    assert response.option_2 == edit_question_model.option_2
    assert response.correct_options == question_only.correct_options

    mock_session.scalars.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_update_question_not_found(mock_session, edit_question_model):
    # Define test data
    question_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Set up the mock session to return None
    mock_session.scalars.return_value.first.return_value = None

    # Call the update_question function and expect a QuizException
    with pytest.raises(CommonException) as exc_info:
        update_question(edit_question_model, question_id, mock_session, user_id)

    # Assert that the exception has the expected properties
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Question does not exist.'
    assert exc_info.value.error_code == 'QUESTION_NOT_FOUND'

    # Verify that the session methods are called with the expected arguments
    mock_session.scalars.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


def test_update_question_db_error(mock_session, question_only, edit_question_model):
    # Define test data
    question_id = question_only.id
    user_id = uuid.uuid4()

    # Set up the mock session to raise an exception
    mock_session.scalars.return_value.first.return_value = question_only
    mock_session.commit.side_effect = Exception('Database error')

    # Call the update_question function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        update_question(edit_question_model, question_id, mock_session, user_id)

    # Assert that the exception has the expected properties
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Question could not be updated. Try later.'

    # Verify that the session methods are called with the expected arguments
    mock_session.scalars.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_not_called()
