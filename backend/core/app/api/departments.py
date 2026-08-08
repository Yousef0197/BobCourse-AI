"""
Departments router — /api/v1/departments
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.services import department_service

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("/", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return department_service.get_all(db)


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return department_service.get_by_id(db, dept_id)


@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return department_service.create(db, body)


@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(dept_id: uuid.UUID, body: DepartmentUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return department_service.update(db, dept_id, body)


@router.delete("/{dept_id}", status_code=204)
def delete_department(dept_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(require_admin)):
    department_service.delete(db, dept_id)
