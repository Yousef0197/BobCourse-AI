"""
Phase 3 — Academic structure service unit tests.
All tests use MagicMock DB — no real DB connection required.
"""
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.college import CollegeCreate, CollegeUpdate
from app.schemas.department import DepartmentCreate
from app.schemas.course import CourseCreate
from app.schemas.semester import SemesterCreate
from app.schemas.course_offering import CourseOfferingCreate
from app.models.user import UserRole


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_db():
    return MagicMock()


def _chain(result):
    """Return a query chain mock that resolves to result."""
    m = MagicMock()
    m.filter.return_value = m
    m.order_by.return_value = m
    m.first.return_value = result
    m.all.return_value = [result] if result else []
    return m


# ─── College service ──────────────────────────────────────────────────────────

class TestCollegeService:
    def test_create_college(self):
        from app.services.college_service import create
        db = _mock_db()
        db.query.return_value = _chain(None)  # no existing code collision

        data = CollegeCreate(name="College of Science", code="COS")
        result = create(db, data)

        db.add.assert_called_once()
        db.commit.assert_called_once()
        assert result.name == "College of Science"
        assert result.code == "COS"

    def test_create_college_duplicate_code_raises_409(self):
        from app.services.college_service import create
        db = _mock_db()
        # Simulate existing college with same code
        existing = SimpleNamespace(code="COS")
        db.query.return_value = _chain(existing)

        with pytest.raises(HTTPException) as exc:
            create(db, CollegeCreate(name="Another", code="COS"))
        assert exc.value.status_code == 409

    def test_get_by_id_not_found_raises_404(self):
        from app.services.college_service import get_by_id
        db = _mock_db()
        db.query.return_value = _chain(None)
        with pytest.raises(HTTPException) as exc:
            get_by_id(db, uuid.uuid4())
        assert exc.value.status_code == 404

    def test_update_college(self):
        from app.services.college_service import update
        existing = SimpleNamespace(id=uuid.uuid4(), name="Old Name", code="OLD")
        db = _mock_db()
        db.query.return_value = _chain(existing)

        result = update(db, existing.id, CollegeUpdate(name="New Name"))
        assert result.name == "New Name"
        db.commit.assert_called_once()

    def test_delete_college(self):
        from app.services.college_service import delete
        existing = SimpleNamespace(id=uuid.uuid4())
        db = _mock_db()
        db.query.return_value = _chain(existing)

        delete(db, existing.id)
        db.delete.assert_called_once_with(existing)
        db.commit.assert_called_once()


# ─── Department service ───────────────────────────────────────────────────────

class TestDepartmentService:
    def test_create_department(self):
        from app.services.department_service import create
        db = _mock_db()

        data = DepartmentCreate(name="Mathematics", code="MATH", college_id=uuid.uuid4())
        result = create(db, data)

        db.add.assert_called_once()
        assert result.name == "Mathematics"

    def test_get_not_found(self):
        from app.services.department_service import get_by_id
        db = _mock_db()
        db.query.return_value = _chain(None)
        with pytest.raises(HTTPException) as exc:
            get_by_id(db, uuid.uuid4())
        assert exc.value.status_code == 404


# ─── Course service ───────────────────────────────────────────────────────────

class TestCourseService:
    def test_create_course(self):
        from app.services.course_service import create
        db = _mock_db()
        db.query.return_value = _chain(None)  # no code collision

        data = CourseCreate(code="CS201", name="Data Structures", credit_hours=3, department_id=uuid.uuid4())
        result = create(db, data)
        assert result.code == "CS201"

    def test_duplicate_code_raises_409(self):
        from app.services.course_service import create
        db = _mock_db()
        db.query.return_value = _chain(SimpleNamespace(code="CS201"))

        with pytest.raises(HTTPException) as exc:
            create(db, CourseCreate(code="CS201", name="Other", credit_hours=3, department_id=uuid.uuid4()))
        assert exc.value.status_code == 409


# ─── Semester service ─────────────────────────────────────────────────────────

class TestSemesterService:
    def test_create_semester(self):
        from app.services.semester_service import create
        from datetime import date
        from app.models.semester import Season
        db = _mock_db()

        data = SemesterCreate(
            name="Spring 2025",
            season=Season.spring,
            year=2025,
            start_date=date(2025, 1, 15),
            end_date=date(2025, 5, 30),
        )
        result = create(db, data)
        assert result.name == "Spring 2025"

    def test_get_not_found(self):
        from app.services.semester_service import get_by_id
        db = _mock_db()
        db.query.return_value = _chain(None)
        with pytest.raises(HTTPException) as exc:
            get_by_id(db, uuid.uuid4())
        assert exc.value.status_code == 404


# ─── Course offering service ──────────────────────────────────────────────────

class TestCourseOfferingService:
    def test_create_requires_instructor_role(self):
        from app.services.course_offering_service import create
        db = _mock_db()
        # Simulate non-instructor user
        student = SimpleNamespace(role=UserRole.student, is_active=True)
        db.query.return_value = _chain(student)

        with pytest.raises(HTTPException) as exc:
            create(db, CourseOfferingCreate(
                course_id=uuid.uuid4(),
                semester_id=uuid.uuid4(),
                instructor_id=uuid.uuid4(),
                section_number="001",
                capacity=30,
            ))
        assert exc.value.status_code == 422

    def test_create_with_valid_instructor(self):
        from app.services.course_offering_service import create
        db = _mock_db()
        instructor = SimpleNamespace(role=UserRole.instructor, is_active=True)
        db.query.return_value = _chain(instructor)

        data = CourseOfferingCreate(
            course_id=uuid.uuid4(),
            semester_id=uuid.uuid4(),
            instructor_id=uuid.uuid4(),
            section_number="002",
            capacity=25,
        )
        result = create(db, data)
        assert result.section_number == "002"
