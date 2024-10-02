import os

from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import UUID4

# Load dotenv file "usually for dev"
load_dotenv()

oauth2_scheme = HTTPBearer()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

class User(BaseModel):
  email: str
  id: UUID4
  is_anonymous: bool


def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
  try:
    data = supabase.auth.get_user(token.credentials)
    user = User(id=data.user.id, email=data.user.email, is_anonymous=data.user.is_anonymous)

    return user
  except Exception as e:
    raise HTTPException(status_code=401, detail="Auth failed")
