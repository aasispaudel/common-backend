from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException

from app.exceptions.common_exception import CommonException
from app.exceptions.error_codes import ErrorCodes
from app.questions.models import QuestionModel, AddQuestionResponse, EditQuestionModel
from app.sql_alchemy.models import Question, Quiz

MAX_QUESTIONS = 10

def add_question(session: Session, question_request: QuestionModel, quiz_id):
  question = Question(question=question_request.question, option_1=question_request.option_1,
                      option_2=question_request.option_2, option_3=question_request.option_3,
                      option_4=question_request.option_4, option_5=question_request.option_5,
                      correct_options=question_request.correct_options,
                      quiz_id=quiz_id)

  try:
    qn_count = session.scalar(
      select(func.count()).select_from(Question).where(Question.quiz_id == quiz_id)
    )

    if qn_count >= MAX_QUESTIONS:
      raise CommonException(status_code=400, detail='Maximum questions limit reached',
                            error_code=ErrorCodes.MAX_QUESTIONS_REACHED)

    session.add(question)
    session.commit()
    session.refresh(question)

    return AddQuestionResponse(question_id=question.id, question_count=qn_count + 1)

  except CommonException as e:
    raise e
  except Exception as e:
    session.rollback()
    raise HTTPException(status_code=500, detail='Could not save right now. Please try again later')


def get_question(qn_id, session):
  try:
    question = session.scalars(
      select(Question).where(Question.id == qn_id)
    ).first()

    if question is None:
      raise CommonException(status_code=404, detail='Question does not exist',
                            error_code=ErrorCodes.QUESTION_NOT_FOUND)

    return QuestionModel.model_validate(question)

  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Question could not be loaded. Try later.')

def update_question(edit_question_model: EditQuestionModel,
                    qn_id: UUID4,
                    session: Session, userid: UUID4):
  try:
    question = session.scalars(
      select(Question).join(Question.quiz)
      .where(Question.id == qn_id).where(Quiz.userid == userid)
    ).first()

    if question is None:
      raise CommonException(status_code=404, detail="Question does not exist.",
                            error_code=ErrorCodes.QUESTION_NOT_FOUND)

    for key, value in edit_question_model.model_dump().items():
      if key in edit_question_model.model_dump(exclude_unset=True):
        if getattr(question, key) != value:
          setattr(question, key, value)

    session.commit()
    session.refresh(question)

    return QuestionModel.model_validate(question)

  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Question could not be updated. Try later.')

def delete_question(qn_id: UUID4, session: Session, userid: UUID4):
  try:
    question = session.scalars(
      select(Question).join(Question.quiz)
      .where(Question.id == qn_id).where(Quiz.userid == userid)
    ).first()

    if question is None:
      raise CommonException(status_code=404, detail="Question does not exist.",
                            error_code=ErrorCodes.QUESTION_NOT_FOUND)

    session.delete(question)
    session.commit()

    return {'id': question.id}

  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not delete questions. Try later.')
