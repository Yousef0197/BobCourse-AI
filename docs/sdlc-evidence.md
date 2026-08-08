# SDLC Evidence

This document provides evidence of each SDLC phase, including outputs, test results, and status.

---

## Phase 0 — Project Bootstrap ✅

**Status:** Complete (pre-existing)

**Outputs:**
- `backend/core/` — FastAPI scaffold with health endpoint
- `backend/analytics/` — Spring Boot scaffold with health endpoint
- `frontend/` — React + Vite + TypeScript scaffold
- `docker-compose.yml`, `.env.example`, `README.md`
- `.github/workflows/ci.yml`

**Test result:** `1 passed in 3.40s` (health endpoint test)

---

## Phase 1 — Database Schema & Python Models ✅

**Status:** Complete

**Outputs:**
- 15 SQLAlchemy ORM models in `backend/core/app/models/`
- 16 Pydantic schema files in `backend/core/app/schemas/`
- Initial Alembic migration: `alembic/versions/8dd7820bb9d1_initial_schema.py`
- Seed script: `backend/core/app/db/seed.py`
- `alembic/env.py` updated to import all models

**Verification:**
```
python -c "import app.models; ..."
Tables registered: 15
['users', 'colleges', 'departments', 'courses', 'semesters', 
 'course_offerings', 'enrollments', 'evaluation_templates', 
 'evaluation_questions', 'evaluation_campaigns', 
 'evaluation_submissions', 'evaluation_answers', 
 'text_comments', 'ai_insights', 'audit_logs']
```

---

## Phase 2 — Authentication & RBAC ✅

**Status:** Complete

**Outputs:**
- `app/core/security.py` — bcrypt password hashing
- `app/core/jwt.py` — JWT creation/validation
- `app/core/deps.py` — FastAPI auth dependencies
- `app/api/auth.py` — POST /api/v1/auth/login
- `tests/test_auth.py` — 15 unit tests

**Test result:** `15 passed`

**Key results:**
- ✅ Login success returns JWT
- ✅ Wrong password → 401
- ✅ Inactive user → 401
- ✅ JWT tamper detected
- ✅ require_admin rejects student (403)

---

## Phase 3 — Academic Structure CRUD ✅

**Status:** Complete

**Outputs:**
- 5 service files, 5 router files
- `tests/test_academic_services.py` — 13 tests

**Test result:** `13 passed in 9.65s`

---

## Phase 4 — Users & Enrollments ✅

**Status:** Complete

**Outputs:**
- `app/services/user_service.py`
- `app/services/enrollment_service.py`
- `app/api/users.py` (includes `/me` endpoint)
- `app/api/enrollments.py`
- `tests/test_users_enrollments.py` — 7 tests

**Test result:** `7 passed in 9.62s`

---

## Phase 5 — Evaluation Templates, Campaigns, Submissions ✅

**Status:** Complete

**Outputs:**
- `app/services/evaluation_template_service.py`
- `app/services/evaluation_campaign_service.py`
- `app/services/submission_service.py`
- All corresponding routers
- `tests/test_evaluation_submissions.py` — 9 tests

**Test result:** `9 passed in 16.58s`

**Business rules verified:**
- ✅ Duplicate submission → 409
- ✅ Non-enrolled student → 403
- ✅ Closed campaign → 403
- ✅ Open campaign creates audit log

---

## Phase 6 — Java Analytics Service ✅

**Status:** Complete

**Outputs:**
- 7 DTOs: `CampaignStatsRequest/Response`, `TrendRequest/Response`, `DashboardRequest/Response`, `CsvExportRequest`
- 4 Services: `CampaignStatsService`, `TrendService`, `DashboardService`, `CsvExportService`
- `AnalyticsController` with 4 endpoints
- 4 JUnit 5 test classes (16 test methods)

**Test result:** `16 passed, 0 failures, 0 errors` — verified with containerized Maven.

---

## Phase 7 — Python → Java Integration ✅

**Status:** Complete

**Outputs:**
- `app/services/analytics_client.py` — httpx client
- `app/services/analytics_service.py` — data fetch + student_id strip
- `app/api/analytics.py` — proxy router with threshold enforcement
- `tests/test_analytics_integration.py` — 9 tests

**Test result:** `9 passed`

**Security verified:** `student_id` never appears in Java payloads; instructor minimum-response thresholds are enforced for analytics and CSV exports; CSV reports contain aggregated statistics only.

---

## Phase 8 — Responsible AI Module ✅

**Status:** Complete

**Outputs:**
- `app/ai/provider_interface.py` — abstract base class
- `app/ai/pii_masking.py` — regex-based PII masker
- `app/ai/offline_fallback.py` — keyword heuristics provider
- `app/ai/openai_provider.py` — guarded GPT provider with offline fallback
- `app/ai/insights_service.py` — orchestration service
- `app/api/ai_insights.py` — router
- `tests/test_responsible_ai.py` — 15 tests

**Test result:** `15 passed in 11.78s`

---

## Phase 9 — React Frontend ✅

**Status:** Complete

**Outputs:**
- `src/lib/apiClient.ts` — JWT injection + 401 redirect
- `src/lib/auth.ts` — token storage utilities
- `src/pages/LoginPage.tsx`
- `src/pages/StudentDashboard.tsx`
- `src/pages/SubmissionForm.tsx`
- `src/pages/InstructorDashboard.tsx`
- `src/pages/AdminDashboard.tsx`
- `src/components/AIInsightsPanel.tsx`
- `src/App.tsx` — routing with role guards

**Verification:**
- TypeScript: `0 errors` (`tsc --noEmit`)
- ESLint: `0 errors, 0 warnings`
- Production build: successful (`142 modules transformed`)

---

## Phase 10 — Documentation ✅

**Status:** Complete

**Outputs:**
- `README.md` (enhanced)
- `docs/architecture.md`
- `docs/database-schema.md`
- `docs/api-documentation.md`
- `docs/security.md`
- `docs/responsible-ai.md`
- `docs/bob-usage-report.md`
- `docs/human-judgment.md`
- `docs/sdlc-evidence.md` (this file)
- `docs/testing-strategy.md`
- `docs/technical-documentation.md`

---

## Final Test Suite

```
======================== 69 passed, 3 warnings ========================
```

All 69 Python tests pass. The Java analytics suite also passes all 16 tests, for 85 automated backend tests in total. 3 deprecation warnings from `python-jose` (utcnow deprecated in Python 3.12+) — these are library warnings, not failures.


