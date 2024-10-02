from fastapi import APIRouter, Depends
from pydantic import UUID4

from app.dependencies.get_session import get_db
from app.dependencies.get_user import get_current_user
from app.questions.models import QuestionModel, EditQuestionModel
from .question_service import add_question, get_question, update_question, delete_question

router = APIRouter(
  prefix="/api/question",
  tags=["Questions"]
)

@router.post("/add/{quiz_id}")
async def add_question_api(question: QuestionModel,
                           quiz_id: UUID4,
                           session=Depends(get_db),
                           user=Depends(get_current_user)):
  question = add_question(session, question, quiz_id)
  return question

@router.get("/{qn_id}")
async def get_question_api(qn_id: UUID4, session=Depends(get_db), user=Depends(get_current_user)):
  return get_question(qn_id, session)

@router.put("/update/{qn_id}")
async def update_question_api(qn_id: UUID4, question: EditQuestionModel, session=Depends(get_db),
                              user=Depends(get_current_user)):
  return update_question(question, qn_id, session, user.id)

@router.delete("/delete/{qn_id}")
async def delete_question_api(qn_id: UUID4, session=Depends(get_db),
                              user=Depends(get_current_user)):
  return delete_question(qn_id, session, user.id)
