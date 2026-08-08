"""
Analytics service — fetches raw data from DB, strips student_id, calls Java.
"""
import uuid
from sqlalchemy.orm import Session

from app.models.evaluation_campaign import EvaluationCampaign
from app.models.evaluation_submission import EvaluationSubmission
from app.models.evaluation_answer import EvaluationAnswer
from app.models.evaluation_question import EvaluationQuestion
from app.models.enrollment import Enrollment
from app.models.course_offering import CourseOffering
from app.models.course import Course
from app.models.semester import Semester
from app.services.analytics_client import analytics_client


def _build_campaign_stats_payload(db: Session, campaign_id: uuid.UUID) -> dict:
    """Build the payload for Java /internal/analytics/campaign-stats."""
    campaign = db.query(EvaluationCampaign).filter(EvaluationCampaign.id == campaign_id).first()
    if not campaign:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    offering = db.query(CourseOffering).filter(CourseOffering.id == campaign.course_offering_id).first()
    course = db.query(Course).filter(Course.id == offering.course_id).first() if offering else None
    semester = db.query(Semester).filter(Semester.id == offering.semester_id).first() if offering else None

    total_enrolled = db.query(Enrollment).filter(
        Enrollment.course_offering_id == campaign.course_offering_id
    ).count()

    submissions = db.query(EvaluationSubmission).filter(
        EvaluationSubmission.campaign_id == campaign_id
    ).all()

    submissions_data = []
    for sub in submissions:
        # student_id intentionally NOT included in Java payload
        answers = db.query(EvaluationAnswer).filter(
            EvaluationAnswer.submission_id == sub.id
        ).all()
        answers_data = []
        for ans in answers:
            question = db.query(EvaluationQuestion).filter(
                EvaluationQuestion.id == ans.question_id
            ).first()
            answers_data.append({
                "questionId": str(ans.question_id),
                "questionText": question.text if question else "",
                "rating": ans.rating,
            })
        submissions_data.append({"answers": answers_data})

    return {
        "campaignId": str(campaign_id),
        "courseCode": course.code if course else "",
        "courseName": course.name if course else "",
        "totalEnrolled": total_enrolled,
        "submissions": submissions_data,
    }


def get_campaign_stats(db: Session, campaign_id: uuid.UUID) -> dict:
    """Fetch campaign data, strip student_id, call Java, return result."""
    payload = _build_campaign_stats_payload(db, campaign_id)
    return analytics_client.campaign_stats(payload)


def get_dashboard(db: Session) -> dict:
    """Build university-wide dashboard payload and call Java."""
    campaigns = db.query(EvaluationCampaign).all()
    campaign_summaries = []

    for campaign in campaigns:
        total_enrolled = db.query(Enrollment).filter(
            Enrollment.course_offering_id == campaign.course_offering_id
        ).count()
        submissions = db.query(EvaluationSubmission).filter(
            EvaluationSubmission.campaign_id == campaign.id
        ).all()
        total_subs = len(submissions)

        # Compute per-campaign average without student_id
        avg_rating = 0.0
        if total_subs > 0:
            all_answers = db.query(EvaluationAnswer).join(
                EvaluationSubmission,
                EvaluationAnswer.submission_id == EvaluationSubmission.id
            ).filter(EvaluationSubmission.campaign_id == campaign.id).all()
            if all_answers:
                avg_rating = sum(a.rating for a in all_answers) / len(all_answers)

        campaign_summaries.append({
            "campaignId": str(campaign.id),
            "status": campaign.status.value,
            "submissions": total_subs,
            "enrolled": total_enrolled,
            "averageRating": round(avg_rating, 2),
        })

    payload = {
        "totalEnrolled": sum(c["enrolled"] for c in campaign_summaries),
        "campaigns": campaign_summaries,
    }
    return analytics_client.dashboard(payload)


def get_course_trends(db: Session, course_id: uuid.UUID) -> dict:
    """Build multi-semester trend payload for a course and call Java."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Find all offerings for this course
    offerings = db.query(CourseOffering).filter(CourseOffering.course_id == course_id).all()
    semesters_data = []

    for offering in offerings:
        semester = db.query(Semester).filter(Semester.id == offering.semester_id).first()
        if not semester:
            continue

        campaign = db.query(EvaluationCampaign).filter(
            EvaluationCampaign.course_offering_id == offering.id
        ).first()
        if not campaign:
            continue

        total_enrolled = db.query(Enrollment).filter(
            Enrollment.course_offering_id == offering.id
        ).count()

        submissions = db.query(EvaluationSubmission).filter(
            EvaluationSubmission.campaign_id == campaign.id
        ).all()
        total_subs = len(submissions)

        # Compute average rating for this semester without student_id
        avg_rating = 0.0
        if total_subs > 0:
            all_answers = db.query(EvaluationAnswer).join(
                EvaluationSubmission,
                EvaluationAnswer.submission_id == EvaluationSubmission.id
            ).filter(EvaluationSubmission.campaign_id == campaign.id).all()
            if all_answers:
                avg_rating = round(sum(a.rating for a in all_answers) / len(all_answers), 2)

        semesters_data.append({
            "semesterId": str(semester.id),
            "semesterName": semester.name,
            "year": semester.year,
            "overallAverage": avg_rating,
            "totalSubmissions": total_subs,
            "totalEnrolled": total_enrolled,
        })

    payload = {
        "courseCode": course.code,
        "courseName": course.name,
        "semesters": semesters_data,
    }
    return analytics_client.course_trends(payload)


def get_csv_export(db: Session, campaign_id: uuid.UUID) -> str:
    """Build CSV export payload (no student_id) and call Java."""
    payload = _build_campaign_stats_payload(db, campaign_id)
    offering = db.query(CourseOffering).filter(
        CourseOffering.id == db.query(EvaluationCampaign).filter(
            EvaluationCampaign.id == campaign_id
        ).first().course_offering_id
    ).first()
    semester = db.query(Semester).filter(Semester.id == offering.semester_id).first() if offering else None

    csv_payload = {
        "campaignId": payload["campaignId"],
        "courseCode": payload["courseCode"],
        "courseName": payload["courseName"],
        "semesterName": semester.name if semester else "",
        "submissions": payload["submissions"],
    }
    return analytics_client.export_csv(csv_payload)
