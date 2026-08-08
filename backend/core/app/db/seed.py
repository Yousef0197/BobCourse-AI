"""
Seed script — creates realistic demo data for all roles.
Run with: python -m app.db.seed

Demo credentials (LOCAL DEVELOPMENT ONLY):
  admin@bobcourse.edu       / Admin1234!
  instructor@bobcourse.edu  / Instructor1234!
  instructor2@bobcourse.edu / Instructor1234!
  student@bobcourse.edu     / Student1234!
  student2@bobcourse.edu    / Student1234!
  student3@bobcourse.edu    / Student1234!
"""
import uuid
import random
from datetime import date, datetime, timezone, timedelta

import bcrypt as _bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
import app.models  # noqa: F401 — register all models
from app.models.user import User, UserRole
from app.models.college import College
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester, Season
from app.models.course_offering import CourseOffering
from app.models.enrollment import Enrollment
from app.models.evaluation_template import EvaluationTemplate
from app.models.evaluation_question import EvaluationQuestion
from app.models.evaluation_campaign import EvaluationCampaign, CampaignStatus
from app.models.evaluation_submission import EvaluationSubmission
from app.models.evaluation_answer import EvaluationAnswer
from app.models.text_comment import TextComment


def _hash(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt(rounds=12)).decode()


def _url(url: str) -> str:
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def seed() -> None:
    engine = create_engine(_url(settings.DATABASE_URL), pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with SessionLocal() as session:
        # ── Idempotency guard ──────────────────────────────────────────────
        if session.query(User).filter_by(email="admin@bobcourse.edu").first():
            print("Seed data already present — skipping.")
            return

        _seed_all(session)
        session.commit()
        print("✓ Seed data created successfully.")
        print("  Accounts (LOCAL DEMO ONLY):")
        print("    admin@bobcourse.edu        / Admin1234!")
        print("    instructor@bobcourse.edu   / Instructor1234!")
        print("    instructor2@bobcourse.edu  / Instructor1234!")
        print("    student@bobcourse.edu      / Student1234!")
        print("    student2@bobcourse.edu     / Student1234!")
        print("    student3@bobcourse.edu     / Student1234!")


def _seed_all(session) -> None:
    now = datetime.now(timezone.utc)

    # ── Colleges ──────────────────────────────────────────────────────
    college_eng = College(id=uuid.uuid4(), name="College of Engineering", code="COE")
    college_sci = College(id=uuid.uuid4(), name="College of Science", code="COS")
    session.add_all([college_eng, college_sci])

    # ── Departments ───────────────────────────────────────────────────
    dept_cs = Department(id=uuid.uuid4(), name="Computer Science", code="CS", college_id=college_eng.id)
    dept_ee = Department(id=uuid.uuid4(), name="Electrical Engineering", code="EE", college_id=college_eng.id)
    dept_math = Department(id=uuid.uuid4(), name="Mathematics", code="MATH", college_id=college_sci.id)
    session.add_all([dept_cs, dept_ee, dept_math])

    # ── Admin ─────────────────────────────────────────────────────────
    admin = User(
        id=uuid.uuid4(), email="admin@bobcourse.edu",
        hashed_password=_hash("Admin1234!"), full_name="System Administrator",
        role=UserRole.admin, is_active=True,
    )

    # ── Instructors ───────────────────────────────────────────────────
    instructor1 = User(
        id=uuid.uuid4(), email="instructor@bobcourse.edu",
        hashed_password=_hash("Instructor1234!"), full_name="Norah",
        role=UserRole.instructor, department_id=dept_cs.id, is_active=True,
    )
    instructor2 = User(
        id=uuid.uuid4(), email="instructor2@bobcourse.edu",
        hashed_password=_hash("Instructor1234!"), full_name="Prof. Ahmed Hassan",
        role=UserRole.instructor, department_id=dept_ee.id, is_active=True,
    )

    # ── Students ──────────────────────────────────────────────────────
    student1 = User(
        id=uuid.uuid4(), email="student@bobcourse.edu",
        hashed_password=_hash("Student1234!"), full_name="Yousef",
        role=UserRole.student, department_id=dept_cs.id, is_active=True,
    )
    student2 = User(
        id=uuid.uuid4(), email="student2@bobcourse.edu",
        hashed_password=_hash("Student1234!"), full_name="Bob Williams",
        role=UserRole.student, department_id=dept_cs.id, is_active=True,
    )
    student3 = User(
        id=uuid.uuid4(), email="student3@bobcourse.edu",
        hashed_password=_hash("Student1234!"), full_name="Carol Davis",
        role=UserRole.student, department_id=dept_cs.id, is_active=True,
    )
    session.add_all([admin, instructor1, instructor2, student1, student2, student3])

    # ── Courses ───────────────────────────────────────────────────────
    cs101 = Course(id=uuid.uuid4(), code="CS101", name="Introduction to Computer Science", credit_hours=3, department_id=dept_cs.id)
    cs201 = Course(id=uuid.uuid4(), code="CS201", name="Data Structures and Algorithms", credit_hours=3, department_id=dept_cs.id)
    ee101 = Course(id=uuid.uuid4(), code="EE101", name="Circuit Analysis", credit_hours=3, department_id=dept_ee.id)
    session.add_all([cs101, cs201, ee101])

    # ── Semesters ─────────────────────────────────────────────────────
    semester_fall2023 = Semester(
        id=uuid.uuid4(), name="Fall 2023", season=Season.fall, year=2023,
        start_date=date(2023, 9, 1), end_date=date(2023, 12, 20), is_active=False,
    )
    semester_fall2024 = Semester(
        id=uuid.uuid4(), name="Fall 2024", season=Season.fall, year=2024,
        start_date=date(2024, 9, 1), end_date=date(2024, 12, 20), is_active=True,
    )
    session.add_all([semester_fall2023, semester_fall2024])
    session.flush()

    # ── Course Offerings ──────────────────────────────────────────────
    # CS101 Fall 2024 — instructor1 (open campaign, for demo submission)
    offering_cs101_f24 = CourseOffering(
        id=uuid.uuid4(), course_id=cs101.id, semester_id=semester_fall2024.id,
        instructor_id=instructor1.id, section_number="001", capacity=30,
    )
    # CS201 Fall 2024 — instructor1 (closed campaign with analytics)
    offering_cs201_f24 = CourseOffering(
        id=uuid.uuid4(), course_id=cs201.id, semester_id=semester_fall2024.id,
        instructor_id=instructor1.id, section_number="001", capacity=25,
    )
    # CS101 Fall 2023 — instructor1 (historical, closed, for trend analysis)
    offering_cs101_f23 = CourseOffering(
        id=uuid.uuid4(), course_id=cs101.id, semester_id=semester_fall2023.id,
        instructor_id=instructor1.id, section_number="001", capacity=30,
    )
    # EE101 Fall 2024 — instructor2
    offering_ee101_f24 = CourseOffering(
        id=uuid.uuid4(), course_id=ee101.id, semester_id=semester_fall2024.id,
        instructor_id=instructor2.id, section_number="001", capacity=20,
    )
    session.add_all([offering_cs101_f24, offering_cs201_f24, offering_cs101_f23, offering_ee101_f24])

    # ── Enrollments ───────────────────────────────────────────────────
    # CS101 Fall 2024: all 3 students
    enroll_s1_cs101 = Enrollment(id=uuid.uuid4(), student_id=student1.id, course_offering_id=offering_cs101_f24.id)
    enroll_s2_cs101 = Enrollment(id=uuid.uuid4(), student_id=student2.id, course_offering_id=offering_cs101_f24.id)
    enroll_s3_cs101 = Enrollment(id=uuid.uuid4(), student_id=student3.id, course_offering_id=offering_cs101_f24.id)
    # CS201 Fall 2024: students 1 and 2
    enroll_s1_cs201 = Enrollment(id=uuid.uuid4(), student_id=student1.id, course_offering_id=offering_cs201_f24.id)
    enroll_s2_cs201 = Enrollment(id=uuid.uuid4(), student_id=student2.id, course_offering_id=offering_cs201_f24.id)
    # CS101 Fall 2023: students 1 and 2 (historical)
    enroll_s1_cs101_f23 = Enrollment(id=uuid.uuid4(), student_id=student1.id, course_offering_id=offering_cs101_f23.id)
    enroll_s2_cs101_f23 = Enrollment(id=uuid.uuid4(), student_id=student2.id, course_offering_id=offering_cs101_f23.id)
    session.add_all([
        enroll_s1_cs101, enroll_s2_cs101, enroll_s3_cs101,
        enroll_s1_cs201, enroll_s2_cs201,
        enroll_s1_cs101_f23, enroll_s2_cs101_f23,
    ])

    # ── Evaluation Template ───────────────────────────────────────────
    template = EvaluationTemplate(
        id=uuid.uuid4(), name="Standard Course Evaluation",
        description="Standard 5-question evaluation form for undergraduate courses.",
        is_active=True, created_by=admin.id,
    )
    session.add(template)
    session.flush()

    questions_data = [
        "How would you rate the overall quality of this course?",
        "How effective was the instructor at explaining concepts?",
        "How well-organised were the course materials?",
        "How challenging did you find the course workload?",
        "How likely are you to recommend this course to another student?",
    ]
    questions = []
    for i, text in enumerate(questions_data):
        q = EvaluationQuestion(
            id=uuid.uuid4(), template_id=template.id,
            text=text, order_index=i, is_required=True,
        )
        session.add(q)
        questions.append(q)
    session.flush()

    # ── Campaigns ─────────────────────────────────────────────────────

    # Campaign 1: CS101 Fall 2024 — OPEN (student can submit demo evaluation)
    campaign_cs101_open = EvaluationCampaign(
        id=uuid.uuid4(), course_offering_id=offering_cs101_f24.id,
        template_id=template.id, status=CampaignStatus.open,
        opens_at=now - timedelta(days=2),
        closes_at=now + timedelta(days=12),
        min_responses_threshold=3,
        created_by=admin.id,
    )

    # Campaign 2: CS201 Fall 2024 — CLOSED with synthetic submissions (analytics demo)
    campaign_cs201_closed = EvaluationCampaign(
        id=uuid.uuid4(), course_offering_id=offering_cs201_f24.id,
        template_id=template.id, status=CampaignStatus.closed,
        opens_at=now - timedelta(days=20),
        closes_at=now - timedelta(days=3),
        min_responses_threshold=2,
        created_by=admin.id,
    )

    # Campaign 3: CS101 Fall 2023 — CLOSED (historical trend data)
    campaign_cs101_f23 = EvaluationCampaign(
        id=uuid.uuid4(), course_offering_id=offering_cs101_f23.id,
        template_id=template.id, status=CampaignStatus.closed,
        opens_at=datetime(2023, 11, 20, tzinfo=timezone.utc),
        closes_at=datetime(2023, 12, 10, tzinfo=timezone.utc),
        min_responses_threshold=2,
        created_by=admin.id,
    )

    # Campaign 4: EE101 Fall 2024 — DRAFT (instructor2's campaign)
    campaign_ee101_draft = EvaluationCampaign(
        id=uuid.uuid4(), course_offering_id=offering_ee101_f24.id,
        template_id=template.id, status=CampaignStatus.draft,
        min_responses_threshold=3,
        created_by=admin.id,
    )

    session.add_all([campaign_cs101_open, campaign_cs201_closed, campaign_cs101_f23, campaign_ee101_draft])
    session.flush()

    # ── Synthetic Submissions for CS201 (closed, for analytics demo) ──
    _add_synthetic_submissions(session, campaign_cs201_closed, [student1, student2], questions, [
        # student1 ratings: [4, 5, 4, 3, 5]
        [4, 5, 4, 3, 5],
        # student2 ratings: [5, 4, 5, 4, 5]
        [5, 4, 5, 4, 5],
    ], [
        "Excellent course! Very well structured and the instructor explains everything clearly.",
        "Great content. The workload was manageable and I learned a lot.",
    ])

    # ── Synthetic Submissions for CS101 Fall 2023 (historical trend) ──
    _add_synthetic_submissions(session, campaign_cs101_f23, [student1, student2], questions, [
        [3, 4, 3, 4, 3],
        [4, 3, 4, 3, 4],
    ], [
        "Good course overall. Some materials could be updated.",
        "Decent introduction. Pacing was a bit fast at times.",
    ])


def _add_synthetic_submissions(session, campaign, students, questions, ratings_grid, comments):
    """Create synthetic submissions with given ratings for a closed campaign."""
    submitted_at_base = datetime.now(timezone.utc) - timedelta(days=5)
    for i, student in enumerate(students):
        sub = EvaluationSubmission(
            id=uuid.uuid4(),
            campaign_id=campaign.id,
            student_id=student.id,
            submitted_at=submitted_at_base + timedelta(hours=i * 3),
        )
        session.add(sub)
        session.flush()

        ratings = ratings_grid[i] if i < len(ratings_grid) else [4, 4, 4, 3, 4]
        for j, q in enumerate(questions):
            session.add(EvaluationAnswer(
                id=uuid.uuid4(),
                submission_id=sub.id,
                question_id=q.id,
                rating=ratings[j] if j < len(ratings) else 4,
            ))

        if i < len(comments) and comments[i]:
            session.add(TextComment(
                id=uuid.uuid4(),
                submission_id=sub.id,
                content=comments[i],
            ))


if __name__ == "__main__":
    seed()

