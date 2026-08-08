"""
Student enrollment view schemas — for /api/v1/me/enrollments.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel

from app.models.evaluation_campaign import CampaignStatus


class CampaignStatusView(BaseModel):
    campaign_id: uuid.UUID | None
    status: CampaignStatus | None
    has_submitted: bool


class EnrolledCourseView(BaseModel):
    enrollment_id: uuid.UUID
    course_offering_id: uuid.UUID
    course_code: str
    course_name: str
    section_number: str
    semester_name: str
    instructor_name: str
    enrolled_at: datetime
    campaign: CampaignStatusView | None

    model_config = {"from_attributes": True}
