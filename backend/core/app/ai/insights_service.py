"""
AI Insights service — orchestrates masking → provider → persist.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.ai.pii_masking import mask_comments
from app.ai.offline_fallback import OfflineFallbackProvider
from app.ai.openai_provider import OpenAIProvider
from app.core.config import settings
from app.models.ai_insight import AIInsight, Sentiment
from app.models.evaluation_campaign import EvaluationCampaign
from app.models.evaluation_submission import EvaluationSubmission
from app.models.text_comment import TextComment


def _get_provider():
    """Select provider based on configuration."""
    if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider()
    return OfflineFallbackProvider()


def trigger_analysis(db: Session, campaign_id: uuid.UUID, actor_id: uuid.UUID) -> AIInsight:
    """
    Trigger AI analysis for a campaign.
    Flow: collect comments → mask PII → run provider → persist insight.
    """
    # Validate campaign exists
    campaign = db.query(EvaluationCampaign).filter(EvaluationCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    # Prevent duplicate analysis
    existing = db.query(AIInsight).filter(AIInsight.campaign_id == campaign_id).first()
    if existing:
        return existing  # return existing insight (idempotent)

    # Collect text comments for this campaign (anonymous — no student_id in join)
    submission_ids = [
        s.id for s in db.query(EvaluationSubmission).filter(
            EvaluationSubmission.campaign_id == campaign_id
        ).all()
    ]
    comments_raw = []
    if submission_ids:
        text_comments = db.query(TextComment).filter(
            TextComment.submission_id.in_(submission_ids)
        ).all()
        comments_raw = [tc.content for tc in text_comments]

    # Mask PII before any AI processing
    masked_comments = mask_comments(comments_raw)

    # Flag any comments that had PII masked
    for tc in (db.query(TextComment).filter(TextComment.submission_id.in_(submission_ids)).all() if submission_ids else []):
        if tc.content != mask_pii_single(tc.content):
            tc.is_flagged = True

    # Run AI analysis
    provider = _get_provider()
    result = provider.analyze(masked_comments)

    # Map sentiment string to enum
    try:
        sentiment_enum = Sentiment(result.sentiment)
    except ValueError:
        sentiment_enum = Sentiment.neutral

    # Persist insight
    insight = AIInsight(
        id=uuid.uuid4(),
        campaign_id=campaign_id,
        summary=result.summary,
        sentiment=sentiment_enum,
        themes=result.themes,
        improvement_areas=result.improvement_areas,
        provider_used=result.provider_used,
        generated_at=datetime.now(timezone.utc),
        human_reviewed=False,
        disclaimer_acknowledged=False,
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


def mask_pii_single(text: str) -> str:
    from app.ai.pii_masking import mask_pii
    return mask_pii(text)


def get_insight(db: Session, campaign_id: uuid.UUID) -> AIInsight:
    insight = db.query(AIInsight).filter(AIInsight.campaign_id == campaign_id).first()
    if not insight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No AI insight found for this campaign")
    return insight


def review_insight(db: Session, insight_id: uuid.UUID, reviewer_id: uuid.UUID) -> AIInsight:
    insight = db.query(AIInsight).filter(AIInsight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI insight not found")
    insight.human_reviewed = True
    insight.reviewed_by = reviewer_id
    insight.reviewed_at = datetime.now(timezone.utc)
    insight.disclaimer_acknowledged = True
    db.commit()
    db.refresh(insight)
    return insight
