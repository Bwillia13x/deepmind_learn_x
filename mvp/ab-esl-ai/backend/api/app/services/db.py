"""Database session management."""

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Import Base here to avoid circular imports
Base = None

def _get_base():
    global Base
    if Base is None:
        from app.models.base import Base as ModelBase
        Base = ModelBase
    return Base

# Use SQLite for testing if DATABASE_URL not set or in test mode
_database_url = settings.database_url
if os.environ.get("ENVIRONMENT") == "test":
    _database_url = "sqlite:///./test.db"

engine = create_engine(
    _database_url,
    pool_pre_ping=True if "postgresql" in _database_url else False,
    connect_args={"check_same_thread": False} if "sqlite" in _database_url else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables."""
    base = _get_base()
    base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager for services."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
