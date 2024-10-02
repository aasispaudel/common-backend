from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse
from dotenv import load_dotenv
from os import getenv

load_dotenv()

username = getenv('PG_USERNAME')
password = getenv('PG_PASSWORD')
host = getenv('PG_HOST')
port = getenv('PG_PORT')
database = getenv('PG_DATABASE_NAME')
# URL-encode the username and password
username = urllib.parse.quote_plus(username)
password = urllib.parse.quote_plus(password)

connection_url = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'

# Create an engine instance (replace with your actual database URL)
engine = create_engine(connection_url)

# Primary database session maker
SessionLocal = sessionmaker(bind=engine)
