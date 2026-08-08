"""
Pydantic schemas for EvaluationQuestion entity.
"""
import uuid
from pydantic import BaseModel, Field


class EvaluationQuestionBase(BaseModel):
    text: str = Field(..., min_length=1)
    order_index: int = Field(..., ge=0)
    is_required: bool = True


class EvaluationQuestionCreate(EvaluationQuestionBase):
    template_id: uuid.UUID


class EvaluationQuestionUpdate(BaseModel):
    text: str | None = Field(None, min_length=1)
    order_index: int | None = Field(None, ge=0)
    is_required: bool | None = None


class EvaluationQuestionResponse(EvaluationQuestionBase):
    id: uuid.UUID
    template_id: uuid.UUID

    model_config = {"from_attributes": True}
