"""
Phase 2 — Auth unit tests.

Tests:
  - login success (admin, instructor, student)
  - wrong password → 401
  - inactive user → 401
  - JWT decode round-trip
  - role guard: require_admin rejects non-admin
"""
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import JWTError

from app.core.jwt import create_access_token, decode_access_token
from app.core.security import hash_password, verify_password
from app.models.user import UserRole


# ─── Security utilities ───────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_and_verify_success(self):
        pw = "SuperSecret123!"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)

    def test_different_hashes_same_password(self):
        """bcrypt generates a unique salt each time."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2
        assert verify_password("same", h1)
        assert verify_password("same", h2)


# ─── JWT ─────────────────────────────────────────────────────────────────────

class TestJWT:
    def test_create_and_decode(self):
        uid = str(uuid.uuid4())
        token = create_access_token(subject=uid, extra_claims={"role": "admin"})
        payload = decode_access_token(token)
        assert payload["sub"] == uid
        assert payload["role"] == "admin"

    def test_invalid_token_raises(self):
        with pytest.raises(JWTError):
            decode_access_token("totally.invalid.token")

    def test_tampered_token_raises(self):
        token = create_access_token(subject=str(uuid.uuid4()))
        tampered = token[:-5] + "AAAAA"
        with pytest.raises(JWTError):
            decode_access_token(tampered)


# ─── Auth endpoint ────────────────────────────────────────────────────────────

def _make_user(role: UserRole, is_active: bool = True, password: str = None):
    """Create a plain namespace acting as a User (no DB, no ORM mapper)."""
    if password is None:
        password = f"{role.value}Pass1!"
    uid = uuid.uuid4()
    return SimpleNamespace(
        id=uid,
        email=f"{role.value}@test.com",
        hashed_password=hash_password(password),
        full_name=f"Test {role.value.capitalize()}",
        role=role,
        department_id=None,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@contextmanager
def _app_with_mock_db(mock_user):
    """Yield a TestClient with the DB dependency overridden to return mock_user."""
    from app.main import app
    from app.db.session import get_db

    def _override_db():
        mock_db = MagicMock()
        query_chain = MagicMock()
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_user
        mock_db.query.return_value = query_chain
        yield mock_db

    app.dependency_overrides[get_db] = _override_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


class TestLoginEndpoint:
    def test_login_success_returns_token(self):
        user = _make_user(UserRole.admin, password="adminPass1!")
        with _app_with_mock_db(user) as client:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": user.email, "password": "adminPass1!"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        payload = decode_access_token(data["access_token"])
        assert payload["sub"] == str(user.id)
        assert payload["role"] == "admin"

    def test_login_wrong_password_returns_401(self):
        user = _make_user(UserRole.instructor, password="correctPass1!")
        with _app_with_mock_db(user) as client:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": user.email, "password": "WRONG_PASSWORD"},
            )
        assert resp.status_code == 401

    def test_login_inactive_user_returns_401(self):
        """Inactive user filtered at DB query → None returned → 401."""
        with _app_with_mock_db(None) as client:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": "inactive@test.com", "password": "anypass"},
            )
        assert resp.status_code == 401

    def test_login_nonexistent_user_returns_401(self):
        with _app_with_mock_db(None) as client:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": "nobody@test.com", "password": "anypass"},
            )
        assert resp.status_code == 401

    def test_student_login_success(self):
        user = _make_user(UserRole.student, password="studentPass1!")
        with _app_with_mock_db(user) as client:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": user.email, "password": "studentPass1!"},
            )
        assert resp.status_code == 200
        payload = decode_access_token(resp.json()["access_token"])
        assert payload["role"] == "student"


# ─── Role guards ─────────────────────────────────────────────────────────────

class TestRoleGuards:
    def test_require_admin_rejects_student(self):
        from app.core.deps import require_admin
        student = _make_user(UserRole.student)
        with pytest.raises(HTTPException) as exc:
            require_admin(current_user=student)
        assert exc.value.status_code == 403

    def test_require_admin_accepts_admin(self):
        from app.core.deps import require_admin
        admin = _make_user(UserRole.admin)
        result = require_admin(current_user=admin)
        assert result is admin

    def test_require_instructor_rejects_admin(self):
        from app.core.deps import require_instructor
        admin = _make_user(UserRole.admin)
        with pytest.raises(HTTPException) as exc:
            require_instructor(current_user=admin)
        assert exc.value.status_code == 403

    def test_require_student_rejects_instructor(self):
        from app.core.deps import require_student
        instructor = _make_user(UserRole.instructor)
        with pytest.raises(HTTPException) as exc:
            require_student(current_user=instructor)
        assert exc.value.status_code == 403
