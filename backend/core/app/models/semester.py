import uuid
import enum

from sqlalchemy import String, Integer, Boolean, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Season(str, enum.Enum):
    fall = "fall"
    spring = "spring"
    summer = "summer"


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    season: Mapped[Season] = mapped_column(Enum(Season, name="season"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date = mapped_column(Date, nullable=False)
    end_date = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    offerings = relationship("CourseOffering", back_populates="semester")
