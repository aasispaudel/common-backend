from pydantic import UUID4
from sqlalchemy import select, func, update
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.exceptions.common_exception import CommonException
from app.exceptions.error_codes import ErrorCodes
from app.global_utils.error_handler import error_handler
from app.quiz.models import QuizRequest, QuizResponse, QuizzesResponse, QuizResponseWithQuestionCount, \
  FullQuizResponse, UpdateQuizRequest
from app.quiz.utils import generate_unique_permalink
from app.sql_alchemy.models import Quiz, Question

MAX_QUIZZES_PER_PAGE = 8


@error_handler
def add_quiz(session: Session, quiz_request: QuizRequest, userid):
  quiz = Quiz(difficulty=quiz_request.difficulty, title=quiz_request.title, userid=userid)

  session.add(quiz)
  session.commit()
  session.refresh(quiz)

  return QuizResponse.model_validate(quiz)


@error_handler
def get_all_quizzes(session: Session, userid, page_no=1):
  quizzes = session.scalars(
    select(Quiz).where(Quiz.userid == userid).order_by(Quiz.created_at.desc())
    .limit(MAX_QUIZZES_PER_PAGE).offset((page_no - 1) * MAX_QUIZZES_PER_PAGE)
  ).all()

  next_url = f'api/quiz/get-all?page={page_no + 1}' if len(quizzes) == MAX_QUIZZES_PER_PAGE \
    else None

  return QuizzesResponse(quizzes=[QuizResponse.model_validate(q) for q in quizzes],
                         next=next_url)


@error_handler
def get_top_quizzes(session: Session):
  quizzes = session.scalars(
    select(Quiz).order_by(Quiz.created_at.desc())
    .limit(MAX_QUIZZES_PER_PAGE)
  ).all()

  return [QuizResponse.model_validate(q) for q in quizzes]

def get_single_quiz(quiz_id, session, userid):
  try:
    quiz = session.execute(
      select(Quiz.id, Quiz.title, Quiz.difficulty, Quiz.link, func.count(Question.id))
      .join(Question, isouter=True)
      .where(Quiz.id == quiz_id).where(Quiz.userid == userid)
      .group_by(Quiz.id, Quiz.title, Quiz.difficulty, Quiz.link)
    ).first()

    if quiz is None:
      raise CommonException(status_code=404, detail='Quiz not found', error_code=ErrorCodes.QUIZ_NOT_FOUND)

    return QuizResponseWithQuestionCount(id=quiz[0],
                                         title=quiz[1],
                                         difficulty=quiz[2],
                                         link=quiz[3],
                                         question_count=quiz[4])

  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not fetch right now. Please try again later')


def publish_quiz(quiz_id: UUID4, session: Session, userid: UUID4):
  try:
    quiz = session.scalars(
      select(Quiz)
      .where(Quiz.id == quiz_id)
      .where(Quiz.userid == userid)
    ).first()

    if quiz is None:
      raise CommonException(status_code=404, detail='Quiz not found', error_code=ErrorCodes.QUIZ_NOT_FOUND)

    if len(quiz.questions) == 0:
      raise CommonException(status_code=400, detail='Cannot publish quiz without any questions',
                            error_code=ErrorCodes.NO_QUESTIONS)

    if quiz.link is not None and quiz.link != '':
      return QuizResponse.model_validate(quiz)

    permalink = generate_unique_permalink(session)
    quiz.link = permalink
    session.commit()
    session.refresh(quiz)

    return QuizResponse.model_validate(quiz)
  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not publish right now. Please try again later')


def get_full_quiz_with_permalink(permalink, session):
  try:
    quiz = session.execute(
      select(Quiz).options(
        joinedload(Quiz.questions)
      ).where(Quiz.link == permalink)
    ).first()

    if quiz is None:
      raise CommonException(status_code=404, detail='Quiz not found', error_code=ErrorCodes.QUIZ_NOT_FOUND)

    return FullQuizResponse.model_validate(quiz[0])

  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not fetch right now. Please try again later')


def get_full_quiz_with_id(quiz_id, session, userid):
  try:
    quiz = session.execute(
      select(Quiz).options(
        joinedload(Quiz.questions)
      ).where(Quiz.id == quiz_id).where(Quiz.userid == userid)
    ).first()

    if quiz is None:
      raise CommonException(status_code=404, detail='Quiz not found', error_code=ErrorCodes.QUIZ_NOT_FOUND)

    return FullQuizResponse.model_validate(quiz[0])

  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not fetch right now. Please try again later')


def update_quiz(quiz_id: UUID4, quiz_model: UpdateQuizRequest, session: Session, userid: UUID4):
  try:
    quiz = session.scalars(
      select(Quiz)
      .where(Quiz.id == quiz_id).where(Quiz.userid == userid)
    ).first()

    if quiz is None:
      raise CommonException(status_code=404, detail='Quiz not found', error_code=ErrorCodes.QUIZ_NOT_FOUND)

    if quiz_model.title is not None and quiz.title != quiz_model.title:
      quiz.title = quiz_model.title
    if quiz_model.difficulty is not None and quiz.difficulty != quiz_model.difficulty:
      quiz.difficulty = quiz_model.difficulty

    session.commit()
    session.refresh(quiz)

    return QuizResponse.model_validate(quiz)
  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not fetch right now. Please try again later')


def delete_quiz(quiz_id: UUID4, session: Session, userid: UUID4):
  try:
    quiz = session.scalars(
      select(Quiz)
      .where(Quiz.id == quiz_id).where(Quiz.userid == userid)
    ).first()

    if quiz is None:
      raise CommonException(status_code=404, detail="Quiz does not exist.",
                            error_code=ErrorCodes.QUIZ_NOT_FOUND)

    session.delete(quiz)
    session.commit()

    return {'id': quiz.id}

  except CommonException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail='Could not delete quiz. Try later.')
