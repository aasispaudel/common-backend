from fastapi import FastAPI, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware

from app.dependencies.get_user import get_current_user
from app.scheduler.scheduler import scheduler
from app.exceptions.common_exception import CommonException
from app.quiz.routes import router as quiz_router
from app.questions.routes import router as question_router
from fastapi.responses import JSONResponse
from app.events.routes import router as event_router

app = FastAPI()

origins = [
  "http://localhost:3000",
  "http://localhost:3001",
  "https://quiz.aasispaudel.pro",
  "https://events.aasispaudel.pro"
]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


app.include_router(quiz_router)
app.include_router(question_router)
app.include_router(event_router)

@app.exception_handler(CommonException)
async def custom_http_exception_handler(request: Request, exc: CommonException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code
        }
    )

@app.get("/hello")
def get_hello():
  return {'greeting': 'Hello world'}


@app.get("/check-user")
def check_user(user=Depends(get_current_user)):
  return user


# Event work with apscheduler
@app.on_event("startup")
async def start_scheduler():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()
