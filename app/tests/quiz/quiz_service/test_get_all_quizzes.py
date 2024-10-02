import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.quiz.quiz_service import get_all_quizzes
from app.quiz.models import QuizResponse, QuizzesResponse
from app.sql_alchemy.models import Quiz
from ...conftest import *
import uuid

def test_get_all_quizzes_success(mocker, mock_session):
    # Fake data
    userid = uuid.uuid4()
    quiz_id1 = uuid.uuid4()
    quiz_id2 = uuid.uuid4()
    quiz_data = [
        Quiz(id=quiz_id1, title="Quiz 1", difficulty="easy", userid=userid),
        Quiz(id=quiz_id2, title="Quiz 2", difficulty="medium", userid=userid)
    ]

    # Mock session.scalars.all
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.return_value.all.return_value = quiz_data

    # Call the get_all_quizzes function
    response = get_all_quizzes(mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert isinstance(response, QuizzesResponse)
    assert len(response.quizzes) == 2
    assert response.quizzes[0].title == "Quiz 1"
    assert response.quizzes[0].id == quiz_id1
    assert response.quizzes[1].title == "Quiz 2"
    assert response.quizzes[1].id == quiz_id2


def test_get_all_quizzes_exception(mocker, mock_session):
    # Fake data
    userid = uuid.uuid4()

    # Mock session.scalars.all to raise an exception
    mock_scalars = mocker.patch.object(mock_session, 'scalars')
    mock_scalars.side_effect = Exception("Database error")

    # Call the get_all_quizzes function and assert exception
    with pytest.raises(HTTPException) as e:
        get_all_quizzes(mock_session, userid)

    # Assertions
    mock_scalars.assert_called_once()
    assert e.value.status_code == 500
    assert e.value.detail == 'Could not fetch right now. Please try again later'
    