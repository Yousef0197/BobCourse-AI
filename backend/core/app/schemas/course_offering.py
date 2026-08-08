"""
Pydantic schemas for CourseOffering entity.
"""
import uuid
from pydantic import BaseModel, Field


class CourseOfferingBase(BaseModel):
    course_id: uuid.UUID
    semester_id: uuid.UUID
    instructor_id: uuid.UUID
    section_number: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., ge=1, le=1000)


class CourseOfferingCreate(CourseOfferingBase):
    pass


class CourseOfferingUpdate(BaseModel):
    instructor_id: uuid.UUID | None = None
    section_number: str | None = Field(None, min_length=1, max_length=20)
    capacity: int | None = Field(None, ge=1, le=1000)


class CourseOfferingResponse(CourseOfferingBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}
