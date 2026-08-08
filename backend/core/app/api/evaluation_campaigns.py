"""
Evaluation campaigns router — /api/v1/evaluation-campaigns
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.models.user import User
from app.schemas.evaluation_campaign import EvaluationCampaignCreate, EvaluationCampaignUpdate, EvaluationCampaignResponse
from app.schemas.evaluation_question import EvaluationQuestionResponse
from app.services import evaluation_campaign_service

router = APIRouter(prefix="/evaluation-campaigns", tags=["evaluation-campaigns"])


@router.get("/", response_model=list[EvaluationCampaignResponse])
def list_campaigns(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return evaluation_campaign_service.get_all(db)


@router.get("/{campaign_id}", response_model=EvaluationCampaignResponse)
def get_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return evaluation_campaign_service.get_by_id(db, campaign_id)


@router.post("/", response_model=EvaluationCampaignResponse, status_code=201)
def create_campaign(body: EvaluationCampaignCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return evaluation_campaign_service.create(db, body, admin.id)


@router.put("/{campaign_id}", response_model=EvaluationCampaignResponse)
def update_campaign(
    campaign_id: uuid.UUID,
    body: EvaluationCampaignUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return evaluation_campaign_service.update_status(db, campaign_id, body, admin.id)


@router.get("/{campaign_id}/questions", response_model=list[EvaluationQuestionResponse])
def get_campaign_questions(campaign_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return evaluation_campaign_service.get_questions_for_campaign(db, campaign_id)
