"""
Evaluation campaigns service — lifecycle management.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.evaluation_campaign import EvaluationCampaign, CampaignStatus
from app.models.evaluation_question import EvaluationQuestion
from app.models.audit_log import AuditLog
from app.schemas.evaluation_campaign import EvaluationCampaignCreate, EvaluationCampaignUpdate


def get_all(db: Session) -> list[EvaluationCampaign]:
    return db.query(EvaluationCampaign).all()


def get_by_id(db: Session, campaign_id: uuid.UUID) -> EvaluationCampaign:
    obj = db.query(EvaluationCampaign).filter(EvaluationCampaign.id == campaign_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return obj


def create(db: Session, data: EvaluationCampaignCreate, created_by: uuid.UUID) -> EvaluationCampaign:
    # One campaign per offering
    if db.query(EvaluationCampaign).filter(
        EvaluationCampaign.course_offering_id == data.course_offering_id
    ).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Campaign already exists for this offering")
    obj = EvaluationCampaign(
        id=uuid.uuid4(),
        course_offering_id=data.course_offering_id,
        template_id=data.template_id,
        status=data.status,
        opens_at=data.opens_at,
        closes_at=data.closes_at,
        min_responses_threshold=data.min_responses_threshold,
        created_by=created_by,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_status(
    db: Session,
    campaign_id: uuid.UUID,
    data: EvaluationCampaignUpdate,
    actor_id: uuid.UUID,
) -> EvaluationCampaign:
    obj = get_by_id(db, campaign_id)
    old_status = obj.status

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    # Write audit log when status transitions to open or closed
    if data.status and data.status != old_status:
        action = None
        if data.status == CampaignStatus.open:
            action = "campaign.opened"
        elif data.status == CampaignStatus.closed:
            action = "campaign.closed"
        if action:
            log = AuditLog(
                id=uuid.uuid4(),
                actor_id=actor_id,
                action=action,
                resource_type="evaluation_campaign",
                resource_id=obj.id,
                details={"from": old_status.value, "to": data.status.value},
            )
            db.add(log)

    db.commit()
    db.refresh(obj)
    return obj


def get_questions_for_campaign(db: Session, campaign_id: uuid.UUID) -> list[EvaluationQuestion]:
    campaign = get_by_id(db, campaign_id)
    return db.query(EvaluationQuestion).filter(
        EvaluationQuestion.template_id == campaign.template_id
    ).order_by(EvaluationQuestion.order_index).all()
