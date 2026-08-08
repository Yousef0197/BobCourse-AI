"""
SQLAlchemy declarative base.
All ORM models must import and extend this Base so Alembic can detect them.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
