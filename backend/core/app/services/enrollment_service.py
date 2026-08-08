"""
Enrollments service.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.schemas.enrollment import EnrollmentCreate


def get_all(db: Session) -> list[Enrollment]:
    return db.query(Enrollment).all()


def get_by_id(db: Session, enrollment_id: uuid.UUID) -> Enrollment:
    obj = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return obj


def get_by_student(db: Session, student_id: uuid.UUID) -> list[Enrollment]:
    return db.query(Enrollment).filter(Enrollment.student_id == student_id).all()


def create(db: Session, data: EnrollmentCreate) -> Enrollment:
    # Validate student role
    student = db.query(User).filter(User.id == data.student_id, User.is_active == True).first()  # noqa: E712
    if not student or student.role != UserRole.student:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="student_id must reference an active user with role=student",
        )
    # Check for duplicate
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == data.student_id,
        Enrollment.course_offering_id == data.course_offering_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already enrolled in this offering")

    obj = Enrollment(id=uuid.uuid4(), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, enrollment_id: uuid.UUID) -> None:
    obj = get_by_id(db, enrollment_id)
    db.delete(obj)
    db.commit()
