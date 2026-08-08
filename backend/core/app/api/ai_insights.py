"""
AI Insights router — /api/v1/ai-insights
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_admin_or_instructor, require_admin, get_db
from app.models.user import User
from app.schemas.ai_insight import AIInsightResponse
from app.ai import insights_service

router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])

_DISCLAIMER = (
    "AI-generated content may be incomplete or inaccurate regardless of the analysis provider used. "
    "Human review is required before acting on these insights. "
    "Student identities cannot be inferred from this output."
)


@router.post("/campaigns/{campaign_id}/trigger", response_model=AIInsightResponse)
def trigger_insight(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Trigger AI analysis for a campaign. Admin only."""
    insight = insights_service.trigger_analysis(db, campaign_id, admin.id)
    return insight


@router.get("/campaigns/{campaign_id}", response_model=AIInsightResponse)
def get_insight(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_instructor),
):
    """View AI insight for a campaign. Returns insight + disclaimer."""
    insight = insights_service.get_insight(db, campaign_id)
    return insight


@router.get("/disclaimer")
def get_disclaimer() -> dict:
    """Return the responsible AI disclaimer text."""
    return {"disclaimer": _DISCLAIMER}


@router.post("/insights/{insight_id}/review", response_model=AIInsightResponse)
def review_insight(
    insight_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Mark an AI insight as human-reviewed. Admin only."""
    return insights_service.review_insight(db, insight_id, admin.id)

