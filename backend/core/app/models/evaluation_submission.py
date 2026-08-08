import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class EvaluationSubmission(Base):
    __tablename__ = "evaluation_submissions"
    __table_args__ = (
        UniqueConstraint("campaign_id", "student_id", name="uq_submission_campaign_student"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evaluation_campaigns.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    campaign = relationship("EvaluationCampaign", back_populates="submissions")
    student = relationship("User", back_populates="evaluation_submissions", foreign_keys=[student_id])
    answers = relationship("EvaluationAnswer", back_populates="submission", cascade="all, delete-orphan")
    text_comment = relationship("TextComment", back_populates="submission", uselist=False, cascade="all, delete-orphan")
