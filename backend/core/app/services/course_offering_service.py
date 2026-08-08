"""
Course offerings service — CRUD operations.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.course_offering import CourseOffering
from app.models.user import User, UserRole
from app.schemas.course_offering import CourseOfferingCreate, CourseOfferingUpdate


def get_all(db: Session) -> list[CourseOffering]:
    return db.query(CourseOffering).all()


def get_by_id(db: Session, offering_id: uuid.UUID) -> CourseOffering:
    obj = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course offering not found")
    return obj


def create(db: Session, data: CourseOfferingCreate) -> CourseOffering:
    # Validate instructor role
    instructor = db.query(User).filter(User.id == data.instructor_id, User.is_active == True).first()  # noqa: E712
    if not instructor or instructor.role != UserRole.instructor:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="instructor_id must reference an active user with role=instructor",
        )
    obj = CourseOffering(id=uuid.uuid4(), **data.model_dump())
    db.add(obj)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Offering with same course/semester/section already exists")
    db.refresh(obj)
    return obj


def update(db: Session, offering_id: uuid.UUID, data: CourseOfferingUpdate) -> CourseOffering:
    obj = get_by_id(db, offering_id)
    if data.instructor_id:
        instructor = db.query(User).filter(User.id == data.instructor_id, User.is_active == True).first()  # noqa: E712
        if not instructor or instructor.role != UserRole.instructor:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="instructor_id must reference an active instructor")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, offering_id: uuid.UUID) -> None:
    obj = get_by_id(db, offering_id)
    db.delete(obj)
    db.commit()
