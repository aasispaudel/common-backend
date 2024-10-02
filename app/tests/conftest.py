import uuid
from unittest.mock import MagicMock

import pytest

from app.quiz.models import QuizRequest
from app.sql_alchemy.models import Quiz, Question, difficulty


@pytest.fixture(scope='function')
def mock_session():
  ms = MagicMock()
  return ms


@pytest.fixture(scope='function')
def quiz_request():
  q = QuizRequest(difficulty="easy", title="Sample Quiz")
  return q

@pytest.fixture(scope='function')
def full_quiz():
  questions = [Question(id=uuid.uuid4(), question="What is the capital of France?",
                        option_1="Paris", option_2="London", option_3="New York", option_4="Berlin",
                        correct_options=["A"]),
               Question(id=uuid.uuid4(), question="What is the capital of Germany?",
                        option_1="Paris", option_2="London", option_3="New York", option_4="Berlin",
                        correct_options=["D"])]
  q = Quiz(id=uuid.uuid4(), title="Sample Quiz", difficulty=difficulty.medium,
           userid=uuid.uuid4(), link=None, questions=questions)

  return q

@pytest.fixture(scope='function')
def quiz_only():
  q = Quiz(id=uuid.uuid4(), title="Sample Quiz", difficulty=difficulty.easy, userid=uuid)
  return q

@pytest.fixture(scope='function')
def question_only():
  q = Question(id=uuid.uuid4(), question="What is the capital of France?",
               option_1="Paris", option_2="London", option_3="New York", option_4="Berlin",
               correct_options=["A"])
  return q
