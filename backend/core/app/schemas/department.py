"""
Pydantic schemas for Department entity.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=20)
    college_id: uuid.UUID


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    code: str | None = Field(None, min_length=1, max_length=20)
    college_id: uuid.UUID | None = None


class DepartmentResponse(DepartmentBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
