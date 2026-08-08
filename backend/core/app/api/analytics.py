"""
Analytics router â€” proxies Python data to Java analytics service.
All endpoints require admin or instructor role.
"""
import uuid
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.deps import require_admin_or_instructor, get_db
from app.models.user import User
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/campaigns/{campaign_id}/stats")
def get_campaign_stats(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_instructor),
) -> dict:
    """
    Get analytics for a campaign.
    Enforces minimum response threshold for instructors.
    """
    result = analytics_service.get_campaign_stats(db, campaign_id)

    # Threshold enforcement: instructors cannot see results below min_responses
    if current_user.role.value == "instructor":
        from app.models.evaluation_campaign import EvaluationCampaign
        campaign = db.query(EvaluationCampaign).filter(EvaluationCampaign.id == campaign_id).first()
        if campaign and result.get("totalSubmissions", 0) < campaign.min_responses_threshold:
            return {
                "message": f"Results not yet available. Minimum {campaign.min_responses_threshold} responses required.",
                "totalSubmissions": result.get("totalSubmissions", 0),
                "threshold": campaign.min_responses_threshold,
            }

    return result


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_instructor),
) -> dict:
    """University-wide KPI dashboard."""
    return analytics_service.get_dashboard(db)


@router.get("/campaigns/{campaign_id}/export-csv")
def export_csv(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_instructor),
):
    """Export aggregated campaign results as CSV."""
    if current_user.role.value == "instructor":
        from fastapi import HTTPException, status
        from app.models.evaluation_campaign import EvaluationCampaign
        from app.models.evaluation_submission import EvaluationSubmission

        campaign = db.query(EvaluationCampaign).filter(
            EvaluationCampaign.id == campaign_id
        ).first()

        if campaign:
            total_submissions = db.query(EvaluationSubmission).filter(
                EvaluationSubmission.campaign_id == campaign_id
            ).count()

            if total_submissions < campaign.min_responses_threshold:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"CSV export is unavailable until at least "
                        f"{campaign.min_responses_threshold} responses are collected."
                    ),
                )

    csv_content = analytics_service.get_csv_export(db, campaign_id)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=campaign-{campaign_id}.csv",
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


@router.get("/courses/{course_id}/trends")
def get_course_trends(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_instructor),
) -> dict:
    """Get multi-semester trend data for a course (via Java)."""
    return analytics_service.get_course_trends(db, course_id)

