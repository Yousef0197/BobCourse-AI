"""initial_schema

Revision ID: 8dd7820bb9d1
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8dd7820bb9d1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    op.execute("CREATE TYPE userrole AS ENUM ('student', 'instructor', 'admin')")
    op.execute("CREATE TYPE season AS ENUM ('fall', 'spring', 'summer')")
    op.execute("CREATE TYPE campaignstatus AS ENUM ('draft', 'open', 'closed')")
    op.execute("CREATE TYPE sentiment AS ENUM ('positive', 'neutral', 'negative', 'mixed')")

    # ── colleges ──────────────────────────────────────────────────────────
    op.create_table(
        'colleges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # ── departments ───────────────────────────────────────────────────────
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('college_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('colleges.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # ── users ─────────────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('student', 'instructor', 'admin', name='userrole', create_type=False), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # ── courses ───────────────────────────────────────────────────────────
    op.create_table(
        'courses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('credit_hours', sa.Integer, nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # ── semesters ─────────────────────────────────────────────────────────
    op.create_table(
        'semesters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('season', postgresql.ENUM('fall', 'spring', 'summer', name='season', create_type=False), nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='false'),
    )

    # ── course_offerings ──────────────────────────────────────────────────
    op.create_table(
        'course_offerings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('semester_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('semesters.id'), nullable=False),
        sa.Column('instructor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('section_number', sa.String(20), nullable=False),
        sa.Column('capacity', sa.Integer, nullable=False),
        sa.UniqueConstraint('course_id', 'semester_id', 'section_number', name='uq_offering_course_semester_section'),
    )

    # ── enrollments ───────────────────────────────────────────────────────
    op.create_table(
        'enrollments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('course_offering_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('course_offerings.id'), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('student_id', 'course_offering_id', name='uq_enrollment_student_offering'),
    )

    # ── evaluation_templates ──────────────────────────────────────────────
    op.create_table(
        'evaluation_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # ── evaluation_questions ──────────────────────────────────────────────
    op.create_table(
        'evaluation_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evaluation_templates.id'), nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('order_index', sa.Integer, nullable=False),
        sa.Column('is_required', sa.Boolean, nullable=False, server_default='true'),
        sa.UniqueConstraint('template_id', 'order_index', name='uq_question_template_order'),
    )

    # ── evaluation_campaigns ──────────────────────────────────────────────
    op.create_table(
        'evaluation_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_offering_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('course_offerings.id'), nullable=False, unique=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evaluation_templates.id'), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'open', 'closed', name='campaignstatus', create_type=False), nullable=False, server_default='draft'),
        sa.Column('opens_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closes_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('min_responses_threshold', sa.Integer, nullable=False, server_default='5'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # ── evaluation_submissions ────────────────────────────────────────────
    op.create_table(
        'evaluation_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evaluation_campaigns.id'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('campaign_id', 'student_id', name='uq_submission_campaign_student'),
    )

    # ── evaluation_answers ────────────────────────────────────────────────
    op.create_table(
        'evaluation_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evaluation_submissions.id'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evaluation_questions.id'), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.UniqueConstraint('submission_id', 'question_id', name='uq_answer_submission_question'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_answer_rating_range'),
    )

    # ── text_comments ─────────────────────────────────────────────────────
    op.create_table(
        'text_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evaluation_submissions.id'), nullable=False, unique=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('is_flagged', sa.Boolean, nullable=False, server_default='false'),
    )

    # ── ai_insights ───────────────────────────────────────────────────────
    op.create_table(
        'ai_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evaluation_campaigns.id'), nullable=False, unique=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('sentiment', postgresql.ENUM('positive', 'neutral', 'negative', 'mixed', name='sentiment', create_type=False), nullable=True),
        sa.Column('themes', postgresql.JSONB, nullable=True),
        sa.Column('improvement_areas', postgresql.JSONB, nullable=True),
        sa.Column('provider_used', sa.String(100), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('human_reviewed', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('disclaimer_acknowledged', sa.Boolean, nullable=False, server_default='false'),
    )

    # ── audit_logs ────────────────────────────────────────────────────────
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('ai_insights')
    op.drop_table('text_comments')
    op.drop_table('evaluation_answers')
    op.drop_table('evaluation_submissions')
    op.drop_table('evaluation_campaigns')
    op.drop_table('evaluation_questions')
    op.drop_table('evaluation_templates')
    op.drop_table('enrollments')
    op.drop_table('course_offerings')
    op.drop_table('semesters')
    op.drop_table('courses')
    op.drop_table('users')
    op.drop_table('departments')
    op.drop_table('colleges')
    op.execute("DROP TYPE IF EXISTS sentiment")
    op.execute("DROP TYPE IF EXISTS campaignstatus")
    op.execute("DROP TYPE IF EXISTS season")
    op.execute("DROP TYPE IF EXISTS userrole")
