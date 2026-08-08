import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class CampaignStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    closed = "closed"


class EvaluationCampaign(Base):
    __tablename__ = "evaluation_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_offering_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("course_offerings.id"), nullable=False, unique=True)
    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evaluation_templates.id"), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus, name="campaignstatus"), default=CampaignStatus.draft, nullable=False)
    opens_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closes_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    min_responses_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    course_offering = relationship("CourseOffering", back_populates="campaign")
    template = relationship("EvaluationTemplate", back_populates="campaigns")
    creator = relationship("User", back_populates="evaluation_campaigns_created", foreign_keys=[created_by])
    submissions = relationship("EvaluationSubmission", back_populates="campaign")
    ai_insight = relationship("AIInsight", back_populates="campaign", uselist=False)
