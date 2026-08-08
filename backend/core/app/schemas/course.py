"""
Pydantic schemas for Course entity.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    credit_hours: int = Field(..., ge=1, le=10)
    department_id: uuid.UUID


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    code: str | None = Field(None, min_length=1, max_length=20)
    name: str | None = Field(None, min_length=1, max_length=255)
    credit_hours: int | None = Field(None, ge=1, le=10)
    department_id: uuid.UUID | None = None


class CourseResponse(CourseBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
