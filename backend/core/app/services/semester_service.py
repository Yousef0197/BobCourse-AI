"""
Semesters service — CRUD operations.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.semester import Semester
from app.schemas.semester import SemesterCreate, SemesterUpdate


def get_all(db: Session) -> list[Semester]:
    return db.query(Semester).order_by(Semester.year.desc(), Semester.season).all()


def get_by_id(db: Session, semester_id: uuid.UUID) -> Semester:
    obj = db.query(Semester).filter(Semester.id == semester_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
    return obj


def create(db: Session, data: SemesterCreate) -> Semester:
    obj = Semester(id=uuid.uuid4(), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, semester_id: uuid.UUID, data: SemesterUpdate) -> Semester:
    obj = get_by_id(db, semester_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, semester_id: uuid.UUID) -> None:
    obj = get_by_id(db, semester_id)
    db.delete(obj)
    db.commit()
