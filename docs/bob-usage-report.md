# Bob Usage Report

## Overview

IBM Bob (AI-assisted software engineer) was used throughout every phase of the BobCourse-AI project. This report documents how Bob contributed and where human judgment was required to correct or guide its output.

---

## Phase 0 — Project Bootstrap

**Bob's contribution:** Generated all scaffold files: `docker-compose.yml`, Python FastAPI scaffold, Java Spring Boot scaffold, React + Vite scaffold, `.env.example`, `.gitignore`, `README.md`, Alembic scaffold, and GitHub Actions CI workflow.

**Human intervention required:**
- Bob attempted to use `psycopg2-binary`, which has no prebuilt wheel for Python 3.13 on Windows. A human recognized this would fail at install time and switched to `psycopg[binary]==3.3.4` (psycopg3).
- Bob's initial Maven verification step claimed the Java scaffold was "verified" without actually running `mvn test` (Maven was not on the local PATH). A human flagged this as a concrete example of AI over-claiming and documented it explicitly.

---

## Phase 1 — Database Schema & Python Models

**Bob's contribution:** Wrote all 15 SQLAlchemy ORM models, 16 Pydantic schema files, the hand-written Alembic migration, and the seed script.

**Human intervention required:**
- Bob initially generated an Alembic migration using `--autogenerate`, which requires a live DB connection. When it failed, Bob correctly pivoted to a hand-written migration — a professional engineering judgment call documented in `docs/human-judgment.md`.
- Bob correctly identified that `%(DATABASE_URL)s` in `alembic.ini` was a ConfigParser interpolation placeholder causing an `InterpolationMissingOptionError`, and fixed it with a hardcoded default.

---

## Phase 2 — Authentication & RBAC

**Bob's contribution:** Wrote JWT utilities (creation, validation), bcrypt security utilities, FastAPI dependency functions (`get_current_user`, role guards), the auth router, and unit tests.

**Human intervention required:**
- Bob initially used `passlib[bcrypt]` for password hashing. Tests immediately failed with a `ValueError: password cannot be longer than 72 bytes` error — a known incompatibility between passlib 1.7.4 and bcrypt 5.0 (the `bcrypt.__about__` attribute was removed). Bob pivoted to calling the `bcrypt` library directly — a correct engineering response to a real dependency conflict.
- Bob used `User.__new__(User)` to create test users without a DB, which failed because SQLAlchemy ORM mappers require `__init__`. Bob corrected this by using `types.SimpleNamespace` objects instead, which is simpler and more correct.
- Bob's `_make_app_with_mock_db` was a generator function used as a context manager without `@contextmanager`. Bob caught and fixed this immediately after the test failure.

---

## Phase 3–5 — Academic Structure, Users, Evaluations

**Bob's contribution:** All five academic structure services + routers, users/enrollments service + router, evaluation template/campaign/submission services + routers, audit logging, and comprehensive unit tests.

**Human oversight:** All tests verified to pass before proceeding. No blocking issues.

---

## Phase 6 — Java Analytics Service

**Bob's contribution:** All Java DTOs, four service classes (CampaignStatsService, TrendService, DashboardService, CsvExportService), the analytics controller, and four JUnit 5 test classes with known-input assertions.

**Human verification:** Maven was not installed directly on the Windows PATH, and the production analytics container intentionally contains only the Java runtime. Instead of relying only on CI, the complete Java test suite was executed locally through a temporary Maven Docker container mounted to the analytics source directory.

**Verified result:** 16 tests passed, 0 failures, 0 errors, with BUILD SUCCESS.

---

## Phase 7 — Python → Java Integration

**Bob's contribution:** `AnalyticsClient` (httpx-based), `analytics_service.py` (data fetching + student_id stripping), analytics router, and integration tests.

**Human security review:** Manual end-to-end testing found two privacy gaps that were not caught by the original implementation:

1. CSV export contained de-identified individual answer rows with `submission_index` instead of aggregated statistics.
2. The instructor analytics page enforced the minimum-response threshold, but the CSV endpoint did not, allowing the threshold to be bypassed through direct export.

Both issues were corrected using regression tests. CSV output now contains aggregated per-question statistics, and instructor CSV export is blocked when the campaign response threshold has not been reached.

**Verified security property:** `student_id` is excluded from analytics payloads sent to Java.

---

## Phase 8 — Responsible AI

**Bob's contribution:** `AIProviderInterface`, `OfflineFallbackProvider`, a guarded `OpenAIProvider` with automatic offline fallback, PII masking utility, insights service, AI insights router, and 15 unit tests.

**Human intervention required:**
- Bob's PII masking applied `_PHONE_RE` before `_STUDENT_ID_RE`, causing the phone regex to consume the `S1234567` pattern before the student ID regex could match it. Two tests failed. Bob diagnosed the root cause (regex ordering) and fixed it by reordering masking operations — student IDs before phone numbers.
- Bob initially wrote a test that expected `"I'm Alice Johnson"` to trigger name masking, but the regex only handles "My name is X" / "I am X" prefix patterns. Rather than making the regex more aggressive (risking false positives on academic text), Bob corrected the test to use the documented trigger phrase.

---

## Phase 9 — React Frontend

**Bob's contribution:** All React pages (Login, StudentDashboard, SubmissionForm, InstructorDashboard, AdminDashboard), the AIInsightsPanel component, auth utilities, and the complete routing tree.

**Human intervention required:**
- Bob declared an unused `RequireAuth` function in `App.tsx`. TypeScript caught this (`TS6133: declared but never read`). Bob removed it to achieve zero TypeScript errors.

---

## Phase 10 — Documentation

**Bob's contribution:** Generated the initial project documentation set, which was later reviewed and updated during human verification.

---

## Summary of Bob's Strengths

1. **Speed:** Generated a broad implementation across all major project phases
2. **Test support:** Produced automated tests that helped expose implementation defects
3. **Architecture support:** Established a clear separation between Python core services and Java analytics
4. **Documentation support:** Produced useful initial technical documentation and project structure

Bob's output still required substantial human review. Manual testing and code inspection identified configuration, migration, frontend state, privacy, CSV export, and authorization issues that were not fully handled by the initial implementation.

## Summary of Human Judgment Required

1. psycopg3 selection for reliable Python compatibility
2. Containerized Maven verification instead of assuming Java tests passed
3. Direct bcrypt usage instead of the incompatible passlib layer
4. SQLAlchemy test-fixture correction using SimpleNamespace
5. Alembic migration and PostgreSQL enum fixes
6. Docker PostgreSQL health-check correction
7. Environment-variable formatting correction
8. Frontend API base URL and Vite environment fixes
9. React Query cache invalidation after evaluation submission
10. Instructor AI-insight permission correction in the frontend
11. CSV redesign from individual de-identified rows to aggregated statistics
12. Backend enforcement of the instructor minimum-response threshold on CSV export
13. Frontend lint and encoding cleanup
14. Dependency-risk review and deliberate avoidance of untested breaking upgrades

See `docs/human-judgment.md` for full decision rationale.





