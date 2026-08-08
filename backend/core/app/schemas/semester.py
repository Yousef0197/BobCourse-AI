"""
Pydantic schemas for Semester entity.
"""
import uuid
from datetime import date
from pydantic import BaseModel, Field, model_validator

from app.models.semester import Season


class SemesterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    season: Season
    year: int = Field(..., ge=2000, le=2100)
    start_date: date
    end_date: date
    is_active: bool = False

    @model_validator(mode="after")
    def end_after_start(self) -> "SemesterBase":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class SemesterCreate(SemesterBase):
    pass


class SemesterUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None


class SemesterResponse(SemesterBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}
