from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base  # re-export for tests expecting Base in this module


# Create a SQLAlchemy engine only if DATABASE_URL is provided.
_engine = create_engine(settings.database_url) if settings.database_url else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine) if _engine else None


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
