"""
Departments service — CRUD operations.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def get_all(db: Session) -> list[Department]:
    return db.query(Department).order_by(Department.name).all()


def get_by_id(db: Session, dept_id: uuid.UUID) -> Department:
    obj = db.query(Department).filter(Department.id == dept_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return obj


def create(db: Session, data: DepartmentCreate) -> Department:
    obj = Department(id=uuid.uuid4(), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, dept_id: uuid.UUID, data: DepartmentUpdate) -> Department:
    obj = get_by_id(db, dept_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, dept_id: uuid.UUID) -> None:
    obj = get_by_id(db, dept_id)
    db.delete(obj)
    db.commit()
