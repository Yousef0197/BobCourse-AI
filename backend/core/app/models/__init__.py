"""
ORM models — import all models here so Alembic autogenerate can detect them.
"""
from app.models.user import User  # noqa: F401
from app.models.college import College  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.course import Course  # noqa: F401
from app.models.semester import Semester  # noqa: F401
from app.models.course_offering import CourseOffering  # noqa: F401
from app.models.enrollment import Enrollment  # noqa: F401
from app.models.evaluation_template import EvaluationTemplate  # noqa: F401
from app.models.evaluation_question import EvaluationQuestion  # noqa: F401
from app.models.evaluation_campaign import EvaluationCampaign  # noqa: F401
from app.models.evaluation_submission import EvaluationSubmission  # noqa: F401
from app.models.evaluation_answer import EvaluationAnswer  # noqa: F401
from app.models.text_comment import TextComment  # noqa: F401
from app.models.ai_insight import AIInsight  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
