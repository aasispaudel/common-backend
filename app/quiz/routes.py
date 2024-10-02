from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import UUID4

from app.dependencies.get_session import get_db
from app.dependencies.get_user import get_current_user
from app.quiz.models import QuizRequest, UpdateQuizRequest
from .quiz_service import add_quiz, get_all_quizzes, get_single_quiz, publish_quiz, get_full_quiz_with_permalink, \
  get_full_quiz_with_id, update_quiz, delete_quiz, get_top_quizzes

router = APIRouter(
  prefix="/api/quiz",
  tags=["Quiz"]
)


@router.post("/add")
async def add_quiz_api(quiz: QuizRequest, session=Depends(get_db), user=Depends(get_current_user)):
  quiz = add_quiz(session, quiz, user.id)
  return quiz


@router.post("/publish/{quiz_id}")
async def publish_quiz_api(quiz_id: UUID4,
                           session=Depends(get_db),
                           user=Depends(get_current_user)):
  quiz = publish_quiz(quiz_id, session, user.id)
  return quiz


@router.get("/get-all")
def get_all_quizzes_api(page: int = 1, session=Depends(get_db),
                        user=Depends(get_current_user)):
  return get_all_quizzes(session, user.id, page)


@router.get("/get-top-quizzes")
def get_all_quizzes_api(session=Depends(get_db)):
  return get_top_quizzes(session)


@router.get("/{quiz_id}")
def get_single_quiz_api(quiz_id: UUID4, session=Depends(get_db), user=Depends(get_current_user)):
  return get_single_quiz(quiz_id, session, user.id)


@router.get("/link/{permalink}")
def get_full_quiz(permalink: Annotated[str, Path(min_length=6, max_length=6)],
                  session=Depends(get_db)):
  return get_full_quiz_with_permalink(permalink, session)


@router.get("/full/{quiz_id}")
def get_full_quiz_with_id_api(quiz_id: UUID4,
                              session=Depends(get_db), user=Depends(get_current_user)):
  return get_full_quiz_with_id(quiz_id, session, user.id)


@router.put("/update/{quiz_id}")
def update_quiz_api(quiz_id: UUID4, quiz: UpdateQuizRequest,
                    session=Depends(get_db), user=Depends(get_current_user)):
  return update_quiz(quiz_id, quiz, session, user.id)


@router.delete("/delete/{quiz_id}")
async def delete_quiz_api(quiz_id: UUID4, session=Depends(get_db),
                          user=Depends(get_current_user)):
  return delete_quiz(quiz_id, session, user.id)
