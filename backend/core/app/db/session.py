"""
SQLAlchemy session factory.
Engine is created lazily on first use so that importing app modules in tests
does not require a running database.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

_engine = None
_SessionLocal = None


def _build_engine_url(url: str) -> str:
    """Normalise postgresql:// to postgresql+psycopg:// for psycopg3 driver."""
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            _build_engine_url(settings.DATABASE_URL),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a database session and ensures it is closed."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
