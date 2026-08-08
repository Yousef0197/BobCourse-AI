"""
Submission service — enforces all business rules:
  1. Student must be enrolled in the campaign's course offering
  2. Campaign must be open
  3. No duplicate submissions
  4. Rating 1-5 (enforced by schema + DB constraint)
  5. Optional text comment (max 2000 chars)
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.evaluation_campaign import EvaluationCampaign, CampaignStatus
from app.models.evaluation_submission import EvaluationSubmission
from app.models.evaluation_answer import EvaluationAnswer
from app.models.enrollment import Enrollment
from app.models.text_comment import TextComment
from app.schemas.submission import SubmissionCreate


def submit(db: Session, data: SubmissionCreate, student_id: uuid.UUID) -> EvaluationSubmission:
    # ── 1. Load campaign ────────────────────────────────────────────────
    campaign = db.query(EvaluationCampaign).filter(EvaluationCampaign.id == data.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    # ── 2. Campaign must be open ─────────────────────────────────────────
    if campaign.status != CampaignStatus.open:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Campaign is not open for submissions",
        )

    # ── 3. Student must be enrolled ──────────────────────────────────────
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_offering_id == campaign.course_offering_id,
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course offering",
        )

    # ── 4. No duplicate submissions ──────────────────────────────────────
    existing = db.query(EvaluationSubmission).filter(
        EvaluationSubmission.campaign_id == data.campaign_id,
        EvaluationSubmission.student_id == student_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted an evaluation for this campaign",
        )

    # ── 5. Create submission ─────────────────────────────────────────────
    submission = EvaluationSubmission(
        id=uuid.uuid4(),
        campaign_id=data.campaign_id,
        student_id=student_id,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    db.flush()

    # ── 6. Create answers ────────────────────────────────────────────────
    for answer in data.answers:
        db.add(EvaluationAnswer(
            id=uuid.uuid4(),
            submission_id=submission.id,
            question_id=answer.question_id,
            rating=answer.rating,
        ))

    # ── 7. Optional text comment ─────────────────────────────────────────
    if data.comment:
        db.add(TextComment(
            id=uuid.uuid4(),
            submission_id=submission.id,
            content=data.comment,
        ))

    db.commit()
    db.refresh(submission)
    return submission


def get_submissions_for_campaign(db: Session, campaign_id: uuid.UUID) -> list[EvaluationSubmission]:
    return db.query(EvaluationSubmission).filter(
        EvaluationSubmission.campaign_id == campaign_id
    ).all()


def get_my_enrollments_with_campaign_status(db: Session, student_id: uuid.UUID) -> list[dict]:
    """
    Returns student's enrolled courses with campaign status and submission flag.
    Used by GET /api/v1/me/enrollments.
    """
    from app.models.course_offering import CourseOffering
    from app.models.course import Course
    from app.models.semester import Semester
    from app.models.user import User

    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    result = []
    for enrollment in enrollments:
        offering = db.query(CourseOffering).filter(CourseOffering.id == enrollment.course_offering_id).first()
        if not offering:
            continue
        course = db.query(Course).filter(Course.id == offering.course_id).first()
        semester = db.query(Semester).filter(Semester.id == offering.semester_id).first()
        instructor = db.query(User).filter(User.id == offering.instructor_id).first()
        campaign = db.query(EvaluationCampaign).filter(
            EvaluationCampaign.course_offering_id == offering.id
        ).first()

        has_submitted = False
        if campaign:
            has_submitted = db.query(EvaluationSubmission).filter(
                EvaluationSubmission.campaign_id == campaign.id,
                EvaluationSubmission.student_id == student_id,
            ).first() is not None

        result.append({
            "enrollment_id": enrollment.id,
            "course_offering_id": offering.id,
            "course_code": course.code if course else "",
            "course_name": course.name if course else "",
            "section_number": offering.section_number,
            "semester_name": semester.name if semester else "",
            "instructor_name": instructor.full_name if instructor else "",
            "enrolled_at": enrollment.enrolled_at,
            "campaign": {
                "campaign_id": campaign.id if campaign else None,
                "status": campaign.status if campaign else None,
                "has_submitted": has_submitted,
            } if campaign else None,
        })
    return result
