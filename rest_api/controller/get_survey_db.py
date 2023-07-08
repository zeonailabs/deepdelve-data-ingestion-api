from typing import Generator

from rest_api.db.db.session import SessionLocal2


def get_db() -> Generator:
    db = SessionLocal2()
    db.current_user_id = None
    try:
        yield db
    finally:
        db.close()