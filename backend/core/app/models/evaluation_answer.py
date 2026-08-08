import uuid

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class EvaluationAnswer(Base):
    __tablename__ = "evaluation_answers"
    __table_args__ = (
        UniqueConstraint("submission_id", "question_id", name="uq_answer_submission_question"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_answer_rating_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evaluation_submissions.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evaluation_questions.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    submission = relationship("EvaluationSubmission", back_populates="answers")
    question = relationship("EvaluationQuestion", back_populates="answers")
