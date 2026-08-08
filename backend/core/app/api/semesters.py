"""
Semesters router — /api/v1/semesters
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.schemas.semester import SemesterCreate, SemesterUpdate, SemesterResponse
from app.services import semester_service

router = APIRouter(prefix="/semesters", tags=["semesters"])


@router.get("/", response_model=list[SemesterResponse])
def list_semesters(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return semester_service.get_all(db)


@router.get("/{semester_id}", response_model=SemesterResponse)
def get_semester(semester_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return semester_service.get_by_id(db, semester_id)


@router.post("/", response_model=SemesterResponse, status_code=201)
def create_semester(body: SemesterCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return semester_service.create(db, body)


@router.put("/{semester_id}", response_model=SemesterResponse)
def update_semester(semester_id: uuid.UUID, body: SemesterUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return semester_service.update(db, semester_id, body)


@router.delete("/{semester_id}", status_code=204)
def delete_semester(semester_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(require_admin)):
    semester_service.delete(db, semester_id)
