"""
Pydantic schemas for EvaluationSubmission and EvaluationAnswer.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    question_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)


class SubmissionCreate(BaseModel):
    campaign_id: uuid.UUID
    answers: list[AnswerCreate] = Field(..., min_length=1)
    comment: str | None = Field(None, max_length=2000)


class EvaluationAnswerResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    rating: int

    model_config = {"from_attributes": True}


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    submitted_at: datetime
    # student_id intentionally omitted from responses

    model_config = {"from_attributes": True}
