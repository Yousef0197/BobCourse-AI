import uuid

from sqlalchemy import Text, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class EvaluationQuestion(Base):
    __tablename__ = "evaluation_questions"
    __table_args__ = (
        UniqueConstraint("template_id", "order_index", name="uq_question_template_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evaluation_templates.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    template = relationship("EvaluationTemplate", back_populates="questions")
    answers = relationship("EvaluationAnswer", back_populates="question")
