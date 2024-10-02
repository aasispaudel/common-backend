import string
import random
from sqlalchemy import select

from app.sql_alchemy.models import Quiz


def generate_permalink_code(length=6):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_permalink(session):
    while True:
        permalink = f'{generate_permalink_code()}'

        does_link_exist = session.execute(
            select(Quiz.id).where(Quiz.link == permalink)
        ).first()

        if not does_link_exist:
            return permalink
