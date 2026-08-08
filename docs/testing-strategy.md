# Testing Strategy

## Overview

BobCourse-AI uses a three-layer testing strategy:

| Layer | Framework | Location | DB Required |
|-------|-----------|----------|-------------|
| Python unit/integration | pytest | `backend/core/tests/` | No |
| Java unit | JUnit 5 | `backend/analytics/src/test/` | No |
| Frontend TypeScript | tsc | `frontend/` | No |

## Python Test Design

### No-Database Strategy

All Python unit tests run without a real PostgreSQL database. This is achieved by:

1. **Lazy engine initialization** — `session.py` creates the engine on first use, not at import time
2. **Dependency injection overrides** — FastAPI's `app.dependency_overrides[get_db]` replaces real DB sessions with `MagicMock` objects
3. **`SimpleNamespace` user objects** — test users are plain Python objects, not SQLAlchemy ORM instances
4. **Mock query chains** — MagicMock objects simulate SQLAlchemy query builder chains

### Test Coverage by Phase

| Phase | Test File | Tests | Coverage |
|-------|-----------|-------|----------|
| Health | `test_health.py` | 1 | Health endpoint |
| Auth              | `test_auth.py`                   | 15     | bcrypt, JWT, login, role guards      |
| Academic | `test_academic_services.py` | 13 | CRUD, validation, 404/409 errors |
| Users/Enrollments | `test_users_enrollments.py` | 7 | User CRUD, enrollment constraints |
| Evaluations | `test_evaluation_submissions.py` | 9 | Business rules, duplicate/403/409 |
| Analytics         | `test_analytics_integration.py`  | 9      | Client, student_id strip, threshold, CSV privacy |
| Responsible AI | `test_responsible_ai.py` | 15 | PII masking, offline fallback |
| **Total**         |                                  | **69** | |

### Critical Business Rules Tested

- ✅ Duplicate submission rejected (409 Conflict)
- ✅ Non-enrolled student rejected (403 Forbidden)
- ✅ Closed campaign rejected (403 Forbidden)
- ✅ student_id never in Java analytics payload
- ✅ Wrong password → 401 Unauthorized
- ✅ Inactive user → 401 Unauthorized
- ✅ Admin-only endpoints reject student/instructor (403)
- ✅ Course offering creation requires instructor role
- ✅ Enrollment creation requires student role
- ✅ Duplicate enrollment rejected (409)
- ✅ Analytics service unavailable → 503
- ✅ Analytics service timeout → 504

## Java Test Design

JUnit 5 unit tests for each service. No database, no Spring context required for service tests. Uses `@BeforeEach` to create service instances directly.

### Java Tests

| Test Class | Methods | What It Tests |
|-----------|---------|---------------|
| `CampaignStatsServiceTest` | 4 | Per-question averages, distributions, response rate, zero enrolled |
| `TrendServiceTest` | 4 | Positive/negative slope, empty semesters, response rate |
| `DashboardServiceTest` | 3 | KPI computation, no campaigns, all closed |
| `CsvExportServiceTest`     | 4       | Aggregated header, per-question aggregation, privacy, CSV escaping |
| `HealthControllerTest` | 1 | Health endpoint (existing) |

**Total Java tests:** 16

**Execution:** Verified locally using containerized Maven and supported by the included Maven Wrapper. Current result: 16 tests passed, 0 failures, 0 errors.

## Frontend Testing

TypeScript strict mode type-checking via:
```bash
npx tsc --noEmit
```

This catches:
- Type mismatches
- Unused variables
- Missing imports
- Incorrect React prop types

**Result:** TypeScript compilation completed successfully.

ESLint verification:

```bash
npm run lint
```

**Result:** 0 errors, 0 warnings.

Production build verification:
```bash
npm run build
```

**Verified result:** 143 modules transformed and production build completed successfully.

## CI/CD Pipeline

`.github/workflows/ci.yml` runs three parallel jobs:

```yaml
python-tests:
  - cd backend/core
  - pip install -r requirements.txt
  - python -m pytest --tb=short -v

java-tests:
  - cd backend/analytics
  - mvn --no-transfer-progress test

lint-frontend:
  - cd frontend
  - npm ci
  - npx tsc --noEmit
  - npm run build
```

## Running Tests Locally

```bash
# Python tests (no DB required)
cd backend/core
python -m pytest --tb=short -v

# Java tests (requires Maven)
cd backend/analytics
./mvnw test

# Frontend TypeScript check
cd frontend
npx tsc --noEmit

# Frontend production build
cd frontend
npm run build
```

## Test Warnings

Three deprecation warnings from `python-jose` library:
```
DeprecationWarning: datetime.datetime.utcnow() is deprecated
```
This is a library issue, not a code issue. The tests pass regardless. The warning will be resolved when python-jose releases a Python 3.12+ compatible version.






