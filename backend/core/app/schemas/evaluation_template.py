"""
Pydantic schemas for EvaluationTemplate entity.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class EvaluationTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    is_active: bool = True


class EvaluationTemplateCreate(EvaluationTemplateBase):
    pass


class EvaluationTemplateUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class EvaluationTemplateResponse(EvaluationTemplateBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
