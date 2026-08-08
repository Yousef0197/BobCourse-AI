"""
Enrollments router — /api/v1/enrollments
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services import enrollment_service

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/", response_model=list[EnrollmentResponse])
def list_enrollments(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return enrollment_service.get_all(db)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_enrollment(enrollment_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return enrollment_service.get_by_id(db, enrollment_id)


@router.post("/", response_model=EnrollmentResponse, status_code=201)
def create_enrollment(body: EnrollmentCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return enrollment_service.create(db, body)


@router.delete("/{enrollment_id}", status_code=204)
def delete_enrollment(enrollment_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    enrollment_service.delete(db, enrollment_id)
