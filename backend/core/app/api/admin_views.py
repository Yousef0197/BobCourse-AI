"""
Admin-facing enriched views router.
Provides denormalized/enriched responses for the admin UI
without polluting the core entity schemas.
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_admin, require_admin_or_instructor, get_current_user, get_db
from app.models.user import User, UserRole
from app.models.evaluation_campaign import EvaluationCampaign
from app.models.course_offering import CourseOffering
from app.models.course import Course
from app.models.semester import Semester
from app.models.evaluation_submission import EvaluationSubmission
from app.models.enrollment import Enrollment

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/campaigns/overview")
def campaigns_overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    """
    Enriched campaign list for admin — includes course name, semester,
    instructor name, and submission count. Admin only.
    """
    campaigns = db.query(EvaluationCampaign).order_by(EvaluationCampaign.created_at.desc()).all()
    result = []
    for c in campaigns:
        offering = db.query(CourseOffering).filter(CourseOffering.id == c.course_offering_id).first()
        course = db.query(Course).filter(Course.id == offering.course_id).first() if offering else None
        semester = db.query(Semester).filter(Semester.id == offering.semester_id).first() if offering else None
        instructor = db.query(User).filter(User.id == offering.instructor_id).first() if offering else None
        sub_count = db.query(EvaluationSubmission).filter(
            EvaluationSubmission.campaign_id == c.id
        ).count()
        enrolled_count = db.query(Enrollment).filter(
            Enrollment.course_offering_id == c.course_offering_id
        ).count()
        result.append({
            "id": str(c.id),
            "status": c.status.value,
            "opens_at": c.opens_at.isoformat() if c.opens_at else None,
            "closes_at": c.closes_at.isoformat() if c.closes_at else None,
            "min_responses_threshold": c.min_responses_threshold,
            "created_at": c.created_at.isoformat(),
            "course_offering_id": str(c.course_offering_id),
            "template_id": str(c.template_id),
            "course_code": course.code if course else "",
            "course_name": course.name if course else "",
            "semester_name": semester.name if semester else "",
            "semester_year": semester.year if semester else None,
            "instructor_name": instructor.full_name if instructor else "",
            "section_number": offering.section_number if offering else "",
            "submission_count": sub_count,
            "enrolled_count": enrolled_count,
        })
    return result


@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """
    Admin dashboard stats: user counts by role, campaign counts.
    Used to supplement Java dashboard KPIs.
    """
    total_students = db.query(User).filter(User.role == UserRole.student, User.is_active == True).count()  # noqa: E712
    total_instructors = db.query(User).filter(User.role == UserRole.instructor, User.is_active == True).count()  # noqa: E712
    total_admins = db.query(User).filter(User.role == UserRole.admin, User.is_active == True).count()  # noqa: E712
    total_courses = db.query(Course).count()
    from app.models.college import College
    from app.models.department import Department
    total_colleges = db.query(College).count()
    total_departments = db.query(Department).count()
    return {
        "totalStudents": total_students,
        "totalInstructors": total_instructors,
        "totalAdmins": total_admins,
        "totalCourses": total_courses,
        "totalColleges": total_colleges,
        "totalDepartments": total_departments,
    }


@router.get("/users")
def list_users_enriched(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    """
    Enriched user list for admin — includes department name.
    """
    from app.models.department import Department
    users = db.query(User).order_by(User.role, User.full_name).all()
    result = []
    for u in users:
        dept = db.query(Department).filter(Department.id == u.department_id).first() if u.department_id else None
        result.append({
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "department_name": dept.name if dept else None,
            "department_id": str(u.department_id) if u.department_id else None,
            "created_at": u.created_at.isoformat(),
        })
    return result


@router.get("/course-offerings/enriched")
def course_offerings_enriched(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_instructor),
) -> list[dict]:
    """
    Course offerings with resolved course name, semester, instructor name.
    Admin sees all; instructor sees only their own.
    """
    query = db.query(CourseOffering)
    if current_user.role == UserRole.instructor:
        query = query.filter(CourseOffering.instructor_id == current_user.id)
    offerings = query.all()
    result = []
    for o in offerings:
        course = db.query(Course).filter(Course.id == o.course_id).first()
        semester = db.query(Semester).filter(Semester.id == o.semester_id).first()
        instructor = db.query(User).filter(User.id == o.instructor_id).first()
        campaign = db.query(EvaluationCampaign).filter(
            EvaluationCampaign.course_offering_id == o.id
        ).first()
        enrolled_count = db.query(Enrollment).filter(
            Enrollment.course_offering_id == o.id
        ).count()
        result.append({
            "id": str(o.id),
            "section_number": o.section_number,
            "capacity": o.capacity,
            "course_id": str(o.course_id),
            "course_code": course.code if course else "",
            "course_name": course.name if course else "",
            "semester_id": str(o.semester_id),
            "semester_name": semester.name if semester else "",
            "semester_year": semester.year if semester else None,
            "instructor_id": str(o.instructor_id),
            "instructor_name": instructor.full_name if instructor else "",
            "enrolled_count": enrolled_count,
            "campaign_id": str(campaign.id) if campaign else None,
            "campaign_status": campaign.status.value if campaign else None,
        })
    return result
