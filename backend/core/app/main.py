from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="BobCourse-AI — Core Service",
    description="University Course Evaluation System — Python Core Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api import auth as auth_router  # noqa: E402
from app.api import colleges, departments, courses, semesters, course_offerings  # noqa: E402
from app.api import users, enrollments  # noqa: E402
from app.api import evaluation_templates, evaluation_campaigns, submissions  # noqa: E402
from app.api import analytics, ai_insights  # noqa: E402
from app.api import admin_views  # noqa: E402

app.include_router(auth_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(colleges.router, prefix=settings.API_V1_PREFIX)
app.include_router(departments.router, prefix=settings.API_V1_PREFIX)
app.include_router(courses.router, prefix=settings.API_V1_PREFIX)
app.include_router(semesters.router, prefix=settings.API_V1_PREFIX)
app.include_router(course_offerings.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(enrollments.router, prefix=settings.API_V1_PREFIX)
app.include_router(evaluation_templates.router, prefix=settings.API_V1_PREFIX)
app.include_router(evaluation_campaigns.router, prefix=settings.API_V1_PREFIX)
app.include_router(submissions.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_insights.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_views.router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Health check endpoint — returns service status."""
    return {"status": "ok", "service": "bobcourse-core"}
