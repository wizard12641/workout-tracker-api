"""Database engine and session management.

The engine is the long-lived connection pool to the database.
SessionLocal is a factory: each call returns a new session, which represents
a unit of work (one request, one transaction).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    future=True,
    )
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
    )