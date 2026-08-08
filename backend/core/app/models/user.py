import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UserRole(str, enum.Enum):
    student = "student"
    instructor = "instructor"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="userrole"), nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    department = relationship("Department", back_populates="users", foreign_keys=[department_id])
    enrollments = relationship("Enrollment", back_populates="student", foreign_keys="Enrollment.student_id")
    course_offerings = relationship("CourseOffering", back_populates="instructor", foreign_keys="CourseOffering.instructor_id")
    evaluation_templates_created = relationship("EvaluationTemplate", back_populates="creator", foreign_keys="EvaluationTemplate.created_by")
    evaluation_campaigns_created = relationship("EvaluationCampaign", back_populates="creator", foreign_keys="EvaluationCampaign.created_by")
    evaluation_submissions = relationship("EvaluationSubmission", back_populates="student", foreign_keys="EvaluationSubmission.student_id")
    audit_logs = relationship("AuditLog", back_populates="actor", foreign_keys="AuditLog.actor_id")
    ai_insights_reviewed = relationship("AIInsight", back_populates="reviewer", foreign_keys="AIInsight.reviewed_by")
