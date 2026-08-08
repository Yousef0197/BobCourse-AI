"""
Colleges service — CRUD operations.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.college import College
from app.schemas.college import CollegeCreate, CollegeUpdate


def get_all(db: Session) -> list[College]:
    return db.query(College).order_by(College.name).all()


def get_by_id(db: Session, college_id: uuid.UUID) -> College:
    obj = db.query(College).filter(College.id == college_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="College not found")
    return obj


def create(db: Session, data: CollegeCreate) -> College:
    if db.query(College).filter(College.code == data.code).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="College code already exists")
    obj = College(id=uuid.uuid4(), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, college_id: uuid.UUID, data: CollegeUpdate) -> College:
    obj = get_by_id(db, college_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, college_id: uuid.UUID) -> None:
    obj = get_by_id(db, college_id)
    db.delete(obj)
    db.commit()
