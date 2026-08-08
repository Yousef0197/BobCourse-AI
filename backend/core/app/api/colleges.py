"""
Colleges router — /api/v1/colleges
  GET    /           → all (authenticated)
  GET    /{id}       → one (authenticated)
  POST   /           → create (admin)
  PUT    /{id}       → update (admin)
  DELETE /{id}       → delete (admin)
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.schemas.college import CollegeCreate, CollegeUpdate, CollegeResponse
from app.services import college_service

router = APIRouter(prefix="/colleges", tags=["colleges"])


@router.get("/", response_model=list[CollegeResponse])
def list_colleges(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return college_service.get_all(db)


@router.get("/{college_id}", response_model=CollegeResponse)
def get_college(college_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return college_service.get_by_id(db, college_id)


@router.post("/", response_model=CollegeResponse, status_code=201)
def create_college(body: CollegeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return college_service.create(db, body)


@router.put("/{college_id}", response_model=CollegeResponse)
def update_college(college_id: uuid.UUID, body: CollegeUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return college_service.update(db, college_id, body)


@router.delete("/{college_id}", status_code=204)
def delete_college(college_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(require_admin)):
    college_service.delete(db, college_id)
