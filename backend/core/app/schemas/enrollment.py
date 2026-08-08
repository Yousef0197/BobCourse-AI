"""
Pydantic schemas for Enrollment entity.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel


class EnrollmentBase(BaseModel):
    student_id: uuid.UUID
    course_offering_id: uuid.UUID


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentResponse(EnrollmentBase):
    id: uuid.UUID
    enrolled_at: datetime

    model_config = {"from_attributes": True}
