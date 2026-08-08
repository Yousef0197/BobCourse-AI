import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import Text, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base


class Sentiment(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    mixed = "mixed"


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evaluation_campaigns.id"), nullable=False, unique=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment: Mapped[Sentiment | None] = mapped_column(Enum(Sentiment, name="sentiment"), nullable=True)
    themes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    improvement_areas: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    provider_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    human_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    disclaimer_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    campaign = relationship("EvaluationCampaign", back_populates="ai_insight")
    reviewer = relationship("User", back_populates="ai_insights_reviewed", foreign_keys=[reviewed_by])
