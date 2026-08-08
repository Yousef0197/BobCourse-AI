"""
Pydantic schemas for AIInsight entity.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel

from app.models.ai_insight import Sentiment


class AIInsightResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    summary: str | None
    sentiment: Sentiment | None
    themes: list | None
    improvement_areas: list | None
    provider_used: str | None
    generated_at: datetime | None
    human_reviewed: bool
    reviewed_by: uuid.UUID | None
    reviewed_at: datetime | None
    disclaimer_acknowledged: bool

    model_config = {"from_attributes": True}


class AIInsightReview(BaseModel):
    human_reviewed: bool = True
    disclaimer_acknowledged: bool = True
