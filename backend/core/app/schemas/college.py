"""
Pydantic schemas for College entity.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class CollegeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=20)


class CollegeCreate(CollegeBase):
    pass


class CollegeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    code: str | None = Field(None, min_length=1, max_length=20)


class CollegeResponse(CollegeBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
