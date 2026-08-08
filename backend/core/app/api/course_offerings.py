"""
Course offerings router — /api/v1/course-offerings
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.schemas.course_offering import CourseOfferingCreate, CourseOfferingUpdate, CourseOfferingResponse
from app.services import course_offering_service

router = APIRouter(prefix="/course-offerings", tags=["course-offerings"])


@router.get("/", response_model=list[CourseOfferingResponse])
def list_offerings(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return course_offering_service.get_all(db)


@router.get("/{offering_id}", response_model=CourseOfferingResponse)
def get_offering(offering_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return course_offering_service.get_by_id(db, offering_id)


@router.post("/", response_model=CourseOfferingResponse, status_code=201)
def create_offering(body: CourseOfferingCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return course_offering_service.create(db, body)


@router.put("/{offering_id}", response_model=CourseOfferingResponse)
def update_offering(offering_id: uuid.UUID, body: CourseOfferingUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return course_offering_service.update(db, offering_id, body)


@router.delete("/{offering_id}", status_code=204)
def delete_offering(offering_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(require_admin)):
    course_offering_service.delete(db, offering_id)
