"""
Phase 4 — Users and enrollment service unit tests.
"""
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.user import UserCreate
from app.schemas.enrollment import EnrollmentCreate
from app.models.user import UserRole


def _chain(result):
    m = MagicMock()
    m.filter.return_value = m
    m.order_by.return_value = m
    m.first.return_value = result
    m.all.return_value = [result] if result else []
    return m


class TestUserService:
    def test_create_user(self):
        from app.services.user_service import create
        db = MagicMock()
        db.query.return_value = _chain(None)

        data = UserCreate(
            email="new@test.com",
            full_name="New User",
            role=UserRole.student,
            password="Pass1234!",
        )
        result = create(db, data)
        db.add.assert_called_once()
        assert result.email == "new@test.com"
        assert result.hashed_password != "Pass1234!"  # bcrypt hash

    def test_create_duplicate_email_raises_409(self):
        from app.services.user_service import create
        db = MagicMock()
        existing = SimpleNamespace(email="dup@test.com")
        db.query.return_value = _chain(existing)

        with pytest.raises(HTTPException) as exc:
            create(db, UserCreate(email="dup@test.com", full_name="X", role=UserRole.student, password="Pass1234!"))
        assert exc.value.status_code == 409

    def test_get_not_found(self):
        from app.services.user_service import get_by_id
        db = MagicMock()
        db.query.return_value = _chain(None)
        with pytest.raises(HTTPException) as exc:
            get_by_id(db, uuid.uuid4())
        assert exc.value.status_code == 404

    def test_update_password(self):
        from app.services.user_service import update
        from app.schemas.user import UserUpdate
        existing = SimpleNamespace(id=uuid.uuid4(), hashed_password="old_hash")
        db = MagicMock()
        db.query.return_value = _chain(existing)

        update(db, existing.id, UserUpdate(password="NewPass1!"))
        assert existing.hashed_password != "old_hash"


class TestEnrollmentService:
    def test_create_enrollment_success(self):
        from app.services.enrollment_service import create
        student = SimpleNamespace(role=UserRole.student, is_active=True)

        call_count = 0
        def query_side_effect(model):
            nonlocal call_count
            m = MagicMock()
            m.filter.return_value = m
            call_count += 1
            if call_count == 1:
                # First call: user lookup
                m.first.return_value = student
            else:
                # Second call: duplicate check
                m.first.return_value = None
            return m

        db = MagicMock()
        db.query.side_effect = query_side_effect

        data = EnrollmentCreate(student_id=uuid.uuid4(), course_offering_id=uuid.uuid4())
        result = create(db, data)
        db.add.assert_called_once()

    def test_enroll_non_student_raises_422(self):
        from app.services.enrollment_service import create
        instructor = SimpleNamespace(role=UserRole.instructor, is_active=True)
        db = MagicMock()
        db.query.return_value = _chain(instructor)

        with pytest.raises(HTTPException) as exc:
            create(db, EnrollmentCreate(student_id=uuid.uuid4(), course_offering_id=uuid.uuid4()))
        assert exc.value.status_code == 422

    def test_duplicate_enrollment_raises_409(self):
        from app.services.enrollment_service import create
        student = SimpleNamespace(role=UserRole.student, is_active=True)
        existing_enrollment = SimpleNamespace(id=uuid.uuid4())

        call_count = 0
        def query_side_effect(model):
            nonlocal call_count
            m = MagicMock()
            m.filter.return_value = m
            call_count += 1
            if call_count == 1:
                m.first.return_value = student
            else:
                m.first.return_value = existing_enrollment
            return m

        db = MagicMock()
        db.query.side_effect = query_side_effect

        with pytest.raises(HTTPException) as exc:
            create(db, EnrollmentCreate(student_id=uuid.uuid4(), course_offering_id=uuid.uuid4()))
        assert exc.value.status_code == 409
