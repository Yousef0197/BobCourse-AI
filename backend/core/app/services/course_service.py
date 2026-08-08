"""
Courses service — CRUD operations.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


def get_all(db: Session) -> list[Course]:
    return db.query(Course).order_by(Course.code).all()


def get_by_id(db: Session, course_id: uuid.UUID) -> Course:
    obj = db.query(Course).filter(Course.id == course_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return obj


def create(db: Session, data: CourseCreate) -> Course:
    if db.query(Course).filter(Course.code == data.code).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course code already exists")
    obj = Course(id=uuid.uuid4(), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, course_id: uuid.UUID, data: CourseUpdate) -> Course:
    obj = get_by_id(db, course_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, course_id: uuid.UUID) -> None:
    obj = get_by_id(db, course_id)
    db.delete(obj)
    db.commit()
