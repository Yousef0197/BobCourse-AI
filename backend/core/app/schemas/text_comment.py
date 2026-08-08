"""
Pydantic schemas for TextComment entity.
"""
import uuid
from pydantic import BaseModel, Field


class TextCommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class TextCommentResponse(TextCommentBase):
    id: uuid.UUID
    submission_id: uuid.UUID
    is_flagged: bool

    model_config = {"from_attributes": True}
