"""
Phase 5 — Evaluation template, campaign, and submission service tests.

Critical business-rule tests:
  - Duplicate submission rejected (409)
  - Non-enrolled student rejected (403)
  - Closed campaign rejected (403)
"""
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.evaluation_campaign import CampaignStatus
from app.models.user import UserRole
from app.schemas.submission import SubmissionCreate, AnswerCreate
from app.schemas.evaluation_template import EvaluationTemplateCreate
from app.schemas.evaluation_campaign import EvaluationCampaignCreate, EvaluationCampaignUpdate


def _chain(result):
    m = MagicMock()
    m.filter.return_value = m
    m.order_by.return_value = m
    m.first.return_value = result
    m.all.return_value = [result] if result else []
    return m


# ─── Template service ─────────────────────────────────────────────────────────

class TestEvaluationTemplateService:
    def test_create_template(self):
        from app.services.evaluation_template_service import create_template
        db = MagicMock()
        data = EvaluationTemplateCreate(name="Test Template")
        result = create_template(db, data, uuid.uuid4())
        assert result.name == "Test Template"
        db.add.assert_called_once()

    def test_get_template_not_found(self):
        from app.services.evaluation_template_service import get_template_by_id
        db = MagicMock()
        db.query.return_value = _chain(None)
        with pytest.raises(HTTPException) as exc:
            get_template_by_id(db, uuid.uuid4())
        assert exc.value.status_code == 404


# ─── Campaign service ─────────────────────────────────────────────────────────

class TestEvaluationCampaignService:
    def test_create_campaign(self):
        from app.services.evaluation_campaign_service import create
        db = MagicMock()
        db.query.return_value = _chain(None)  # no existing campaign

        data = EvaluationCampaignCreate(
            course_offering_id=uuid.uuid4(),
            template_id=uuid.uuid4(),
        )
        result = create(db, data, uuid.uuid4())
        assert result.status == CampaignStatus.draft

    def test_duplicate_campaign_raises_409(self):
        from app.services.evaluation_campaign_service import create
        db = MagicMock()
        existing = SimpleNamespace(id=uuid.uuid4())
        db.query.return_value = _chain(existing)

        with pytest.raises(HTTPException) as exc:
            create(db, EvaluationCampaignCreate(course_offering_id=uuid.uuid4(), template_id=uuid.uuid4()), uuid.uuid4())
        assert exc.value.status_code == 409

    def test_open_campaign_creates_audit_log(self):
        from app.services.evaluation_campaign_service import update_status
        campaign = SimpleNamespace(
            id=uuid.uuid4(),
            status=CampaignStatus.draft,
            template_id=uuid.uuid4(),
        )
        db = MagicMock()
        db.query.return_value = _chain(campaign)

        update_status(db, campaign.id, EvaluationCampaignUpdate(status=CampaignStatus.open), uuid.uuid4())
        # Should have added 1 item (the audit log)
        assert db.add.called


# ─── Submission service — business rules ──────────────────────────────────────

class TestSubmissionService:
    def _make_open_campaign(self, offering_id=None):
        if offering_id is None:
            offering_id = uuid.uuid4()
        return SimpleNamespace(
            id=uuid.uuid4(),
            status=CampaignStatus.open,
            course_offering_id=offering_id,
        )

    def test_duplicate_submission_raises_409(self):
        from app.services.submission_service import submit
        campaign = self._make_open_campaign()
        enrollment = SimpleNamespace(id=uuid.uuid4())
        existing_submission = SimpleNamespace(id=uuid.uuid4())

        call_count = 0
        def query_side_effect(model):
            nonlocal call_count
            m = MagicMock()
            m.filter.return_value = m
            call_count += 1
            if call_count == 1:
                m.first.return_value = campaign     # get campaign
            elif call_count == 2:
                m.first.return_value = enrollment   # enrollment check
            else:
                m.first.return_value = existing_submission  # duplicate check
            return m

        db = MagicMock()
        db.query.side_effect = query_side_effect

        with pytest.raises(HTTPException) as exc:
            submit(db, SubmissionCreate(
                campaign_id=campaign.id,
                answers=[AnswerCreate(question_id=uuid.uuid4(), rating=4)],
            ), uuid.uuid4())
        assert exc.value.status_code == 409

    def test_non_enrolled_student_raises_403(self):
        from app.services.submission_service import submit
        campaign = self._make_open_campaign()

        call_count = 0
        def query_side_effect(model):
            nonlocal call_count
            m = MagicMock()
            m.filter.return_value = m
            call_count += 1
            if call_count == 1:
                m.first.return_value = campaign   # get campaign
            else:
                m.first.return_value = None       # not enrolled
            return m

        db = MagicMock()
        db.query.side_effect = query_side_effect

        with pytest.raises(HTTPException) as exc:
            submit(db, SubmissionCreate(
                campaign_id=campaign.id,
                answers=[AnswerCreate(question_id=uuid.uuid4(), rating=3)],
            ), uuid.uuid4())
        assert exc.value.status_code == 403

    def test_closed_campaign_raises_403(self):
        from app.services.submission_service import submit
        closed_campaign = SimpleNamespace(
            id=uuid.uuid4(),
            status=CampaignStatus.closed,
            course_offering_id=uuid.uuid4(),
        )
        db = MagicMock()
        db.query.return_value = _chain(closed_campaign)

        with pytest.raises(HTTPException) as exc:
            submit(db, SubmissionCreate(
                campaign_id=closed_campaign.id,
                answers=[AnswerCreate(question_id=uuid.uuid4(), rating=5)],
            ), uuid.uuid4())
        assert exc.value.status_code == 403

    def test_successful_submission(self):
        from app.services.submission_service import submit
        student_id = uuid.uuid4()
        offering_id = uuid.uuid4()
        campaign = self._make_open_campaign(offering_id)
        enrollment = SimpleNamespace(id=uuid.uuid4())

        call_count = 0
        def query_side_effect(model):
            nonlocal call_count
            m = MagicMock()
            m.filter.return_value = m
            call_count += 1
            if call_count == 1:
                m.first.return_value = campaign
            elif call_count == 2:
                m.first.return_value = enrollment
            else:
                m.first.return_value = None  # no duplicate
            return m

        db = MagicMock()
        db.query.side_effect = query_side_effect

        result = submit(db, SubmissionCreate(
            campaign_id=campaign.id,
            answers=[
                AnswerCreate(question_id=uuid.uuid4(), rating=5),
                AnswerCreate(question_id=uuid.uuid4(), rating=4),
            ],
            comment="Great course!",
        ), student_id)

        assert result.campaign_id == campaign.id
        assert result.student_id == student_id
