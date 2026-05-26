"""Declarative base class for all SQLAlchemy ORM models.

Every model in this application inherits from `Base`. This is what
SQLAlchemy uses to discover models and build the metadata registry.
"""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass