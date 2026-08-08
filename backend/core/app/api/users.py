"""
Users router — /api/v1/users (admin CRUD)
Me router — /api/v1/me (own profile)
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPublic
from app.services import user_service

router = APIRouter(tags=["users"])


# ── /api/v1/me ────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user's own profile."""
    return current_user


# ── /api/v1/users (admin CRUD) ────────────────────────────────────────────────

@router.get("/users", response_model=list[UserPublic])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return user_service.get_all(db)


@router.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return user_service.get_by_id(db, user_id)


@router.post("/users", response_model=UserPublic, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return user_service.create(db, body)


@router.put("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: uuid.UUID, body: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return user_service.update(db, user_id, body)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user_service.delete(db, user_id)
