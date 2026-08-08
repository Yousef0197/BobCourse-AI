"""
Users service — Admin CRUD.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_all(db: Session) -> list[User]:
    return db.query(User).order_by(User.email).all()


def get_by_id(db: Session, user_id: uuid.UUID) -> User:
    obj = db.query(User).filter(User.id == user_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return obj


def create(db: Session, data: UserCreate) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    obj = User(
        id=uuid.uuid4(),
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        department_id=data.department_id,
        is_active=data.is_active,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, user_id: uuid.UUID, data: UserUpdate) -> User:
    obj = get_by_id(db, user_id)
    fields = data.model_dump(exclude_unset=True)
    if "password" in fields:
        obj.hashed_password = hash_password(fields.pop("password"))
    for field, value in fields.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, user_id: uuid.UUID) -> None:
    obj = get_by_id(db, user_id)
    db.delete(obj)
    db.commit()
