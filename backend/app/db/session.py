from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_engine = None
_SessionLocal = None

def _init(url: str):
    global _engine, _SessionLocal
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    _engine = create_engine(url, **kwargs)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

def get_db():
    if _SessionLocal is None:
        from app.config import settings
        _init(settings.database_url)
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
