"""
Evaluation templates + questions router — /api/v1/evaluation-templates
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, get_db
from app.models.user import User
from app.schemas.evaluation_template import EvaluationTemplateCreate, EvaluationTemplateUpdate, EvaluationTemplateResponse
from app.schemas.evaluation_question import EvaluationQuestionCreate, EvaluationQuestionUpdate, EvaluationQuestionResponse
from app.services import evaluation_template_service

router = APIRouter(prefix="/evaluation-templates", tags=["evaluation-templates"])


@router.get("/", response_model=list[EvaluationTemplateResponse])
def list_templates(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return evaluation_template_service.get_all_templates(db)


@router.get("/{template_id}", response_model=EvaluationTemplateResponse)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return evaluation_template_service.get_template_by_id(db, template_id)


@router.post("/", response_model=EvaluationTemplateResponse, status_code=201)
def create_template(body: EvaluationTemplateCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return evaluation_template_service.create_template(db, body, admin.id)


@router.put("/{template_id}", response_model=EvaluationTemplateResponse)
def update_template(template_id: uuid.UUID, body: EvaluationTemplateUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return evaluation_template_service.update_template(db, template_id, body)


@router.get("/{template_id}/questions", response_model=list[EvaluationQuestionResponse])
def get_questions(template_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return evaluation_template_service.get_questions_for_template(db, template_id)


@router.post("/{template_id}/questions", response_model=EvaluationQuestionResponse, status_code=201)
def add_question(
    template_id: uuid.UUID,
    body: EvaluationQuestionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    body.template_id = template_id
    return evaluation_template_service.add_question(db, body)


@router.put("/{template_id}/questions/{question_id}", response_model=EvaluationQuestionResponse)
def update_question(
    template_id: uuid.UUID,
    question_id: uuid.UUID,
    body: EvaluationQuestionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return evaluation_template_service.update_question(db, question_id, body)


@router.delete("/{template_id}/questions/{question_id}", status_code=204)
def delete_question(template_id: uuid.UUID, question_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    evaluation_template_service.delete_question(db, question_id)
