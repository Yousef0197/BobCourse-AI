"""
Submissions router — /api/v1/submissions
Me enrollments — /api/v1/me/enrollments
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_student, get_db
from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.schemas.me import EnrolledCourseView
from app.services import submission_service

router = APIRouter(tags=["submissions"])


@router.get("/me/enrollments", response_model=list[EnrolledCourseView])
def my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
) -> list:
    """Student's enrolled courses with campaign status."""
    return submission_service.get_my_enrollments_with_campaign_status(db, current_user.id)


@router.post("/submissions", response_model=SubmissionResponse, status_code=201)
def create_submission(
    body: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
) -> SubmissionResponse:
    """Submit an evaluation. Enforces enrollment, open campaign, no duplicates."""
    return submission_service.submit(db, body, current_user.id)
