from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI para obtener la sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
