"""
Pydantic schemas for EvaluationCampaign entity.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.evaluation_campaign import CampaignStatus


class EvaluationCampaignBase(BaseModel):
    course_offering_id: uuid.UUID
    template_id: uuid.UUID
    status: CampaignStatus = CampaignStatus.draft
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    min_responses_threshold: int = Field(5, ge=1)


class EvaluationCampaignCreate(EvaluationCampaignBase):
    pass


class EvaluationCampaignUpdate(BaseModel):
    status: CampaignStatus | None = None
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    min_responses_threshold: int | None = Field(None, ge=1)


class EvaluationCampaignResponse(EvaluationCampaignBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
