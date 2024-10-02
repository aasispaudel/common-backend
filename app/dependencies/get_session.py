from app.sql_alchemy.alchemy import SessionLocal

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
