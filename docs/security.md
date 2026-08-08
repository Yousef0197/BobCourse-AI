# Security

## Authentication

- **Algorithm:** JWT HS256
- **Token lifetime:** 60 minutes (access token)
- **Payload:** `sub` (user UUID), `role`, `email`, `iat`, `exp`, `jti`
- **Storage:** `localStorage` in browser (frontend)
- **Header:** `Authorization: Bearer <token>`

## Password Hashing

- **Algorithm:** bcrypt
- **Cost factor:** 12 (intentionally slow to resist brute force)
- **Implementation:** direct `bcrypt` library (not passlib, which has compatibility issues with bcrypt ≥ 4.1 on Python 3.13)
- Passwords are never stored or logged in plaintext

## Role-Based Access Control (RBAC)

| Role | Permissions |
|------|------------|
| `student` | Login, view own enrollments, submit one evaluation per open campaign |
| `instructor` | Login, view own profile, view anonymized evaluation results (with threshold) |
| `admin` | Full system access — CRUD on all entities, analytics, AI insights, audit logs |

Every protected endpoint uses a FastAPI `Depends()` guard:
- `get_current_user` — validates JWT, loads user from DB
- `require_admin` — 403 if not admin
- `require_instructor` — 403 if not instructor
- `require_student` — 403 if not student
- `require_admin_or_instructor` — 403 if neither

## Anonymity Enforcement

1. **`evaluation_submissions.student_id`** is stored only for:
   - UNIQUE constraint enforcement (one submission per student per campaign)
   - Admin abuse investigation (never exposed in analytics)

2. **Instructor-facing API endpoints** never return `student_id`

3. **Java analytics service** never receives `student_id` — Python strips it before every call

4. **`text_comments`** has no student reference — linked only to `submission_id`

5. **Minimum response threshold** — configurable per campaign with a default of 5. Instructors cannot view analytics or export CSV reports until the configured threshold is met.

6. **Aggregated CSV reports** — exports contain per-question averages and rating distributions rather than individual submission rows or submission indexes.

## Input Validation

- All request bodies validated by Pydantic schemas
- Rating must be 1–5 (Pydantic `ge=1, le=5` + database `CHECK` constraint)
- Text comment max 2000 characters
- Email format validated by Pydantic `EmailStr`
- Password minimum 8 characters
- UUID path parameters validated by FastAPI

## Additional Security Measures

- CORS configured to allow only the frontend origin
- `pool_pre_ping=True` on SQLAlchemy engine (prevents stale connections)
- AI insights carry a mandatory disclaimer
- Production secrets such as SECRET_KEY are supplied through environment variables. Demo-only credentials are intentionally defined in seed.py for local demonstration and must not be used in production.
- `.env.example` provided with placeholder values only

## Security Checklist

- [x] bcrypt password hashing (cost 12)
- [x] JWT RBAC enforced server-side on every protected endpoint
- [x] student_id never returned through instructor-facing endpoints
- [x] student_id never sent to Java analytics service
- [x] Configurable minimum response threshold enforced for instructor analytics and CSV export
- [x] CSV reports contain aggregated statistics only
- [x] Input validation on all inputs
- [x] No production secrets hardcoded in source; demo seed credentials are clearly identified as non-production
- [x] Demo credentials documented (not production)


## Known and Accepted Risks

- The production dependency audit currently reports two moderate React Router advisories.
- Navigation in BobCourse-AI uses internal application routes; no user-controlled external redirect target is passed to `navigate()`.
- Major dependency upgrades were intentionally not forced immediately before submission because they could introduce breaking changes. These dependencies should be upgraded and regression-tested in the next maintenance cycle.
- JWT access tokens are stored in browser `localStorage` for this MVP. Production deployment should apply strict XSS protections and preferably evaluate secure HttpOnly cookies for stronger token protection.

