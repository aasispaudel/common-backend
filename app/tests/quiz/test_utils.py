from unittest.mock import MagicMock
import pytest
from app.quiz import utils

def test_generate_unique_permalink_single_link(mocker):
  session = MagicMock()

  # Spy on generate_permalink_code to assert its values
  spy = mocker.spy(utils, 'generate_permalink_code')

  # Mock the session.execute method to simulate database behavior
  mock_execute = mocker.patch.object(session, 'execute')
  mock_execute.side_effect = [
    MagicMock(first=MagicMock(return_value=None))  # First call returns unique link existence
  ]

  result = utils.generate_unique_permalink(session)

  assert result is not None
  assert result.islower()
  assert len(result) == 6
  assert result.isalnum()

  assert spy.call_count == 1


def test_generate_unique_permalink_many_link(mocker):
  session = MagicMock()

  # Spy on generate_permalink_code to assert its values
  spy = mocker.spy(utils, 'generate_permalink_code')

  # Mock the session.execute method to simulate database behavior
  mock_execute = mocker.patch.object(session, 'execute')
  mock_execute.side_effect = [
    MagicMock(first=MagicMock(return_value=['row'])),  # First call returns link already exists
    MagicMock(first=MagicMock(return_value=['row 2'])),  # Second call returns link already exists
    MagicMock(first=MagicMock(return_value=None))  # Second call returns unique link existence
  ]

  result = utils.generate_unique_permalink(session)

  assert result is not None
  assert result.islower()
  assert len(result) == 6
  assert result.isalnum()

  assert spy.call_count == 3
