"""
Evaluation templates service.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.evaluation_template import EvaluationTemplate
from app.models.evaluation_question import EvaluationQuestion
from app.schemas.evaluation_template import EvaluationTemplateCreate, EvaluationTemplateUpdate
from app.schemas.evaluation_question import EvaluationQuestionCreate, EvaluationQuestionUpdate


# ─── Templates ────────────────────────────────────────────────────────────────

def get_all_templates(db: Session) -> list[EvaluationTemplate]:
    return db.query(EvaluationTemplate).order_by(EvaluationTemplate.name).all()


def get_template_by_id(db: Session, template_id: uuid.UUID) -> EvaluationTemplate:
    obj = db.query(EvaluationTemplate).filter(EvaluationTemplate.id == template_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return obj


def create_template(db: Session, data: EvaluationTemplateCreate, created_by: uuid.UUID) -> EvaluationTemplate:
    obj = EvaluationTemplate(
        id=uuid.uuid4(),
        name=data.name,
        description=data.description,
        is_active=data.is_active,
        created_by=created_by,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_template(db: Session, template_id: uuid.UUID, data: EvaluationTemplateUpdate) -> EvaluationTemplate:
    obj = get_template_by_id(db, template_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


# ─── Questions ────────────────────────────────────────────────────────────────

def add_question(db: Session, data: EvaluationQuestionCreate) -> EvaluationQuestion:
    # Validate template exists
    get_template_by_id(db, data.template_id)
    obj = EvaluationQuestion(id=uuid.uuid4(), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_question(db: Session, question_id: uuid.UUID, data: EvaluationQuestionUpdate) -> EvaluationQuestion:
    obj = db.query(EvaluationQuestion).filter(EvaluationQuestion.id == question_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_question(db: Session, question_id: uuid.UUID) -> None:
    obj = db.query(EvaluationQuestion).filter(EvaluationQuestion.id == question_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    db.delete(obj)
    db.commit()


def get_questions_for_template(db: Session, template_id: uuid.UUID) -> list[EvaluationQuestion]:
    get_template_by_id(db, template_id)
    return db.query(EvaluationQuestion).filter(
        EvaluationQuestion.template_id == template_id
    ).order_by(EvaluationQuestion.order_index).all()
