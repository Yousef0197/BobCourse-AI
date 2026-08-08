"""
Courses router — /api/v1/courses
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[CourseResponse])
def list_courses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return course_service.get_all(db)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return course_service.get_by_id(db, course_id)


@router.post("/", response_model=CourseResponse, status_code=201)
def create_course(body: CourseCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return course_service.create(db, body)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: uuid.UUID, body: CourseUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return course_service.update(db, course_id, body)


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(require_admin)):
    course_service.delete(db, course_id)
