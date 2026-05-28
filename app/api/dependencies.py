"""FastAPI dependency-injection functions.

These provide injectable dependencies for routes — database sessions,
settings, and (later) the authenticated user. Each function is used with
FastAPI's `Depends()` mechanism in route signatures.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.config import get_settings, Settings
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Yield a database session for one request.

    A session is created when the request starts and closed when it
    finishes — regardless of whether the request raised an exception.
    This is the standard FastAPI/SQLAlchemy unit-of-work pattern.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()