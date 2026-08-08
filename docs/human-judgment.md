# Human Judgment Decisions

This document records all significant engineering decisions made during development where human judgment was required to correct AI output, resolve ambiguity, or make an architectural trade-off.

---

## Decision 1: psycopg3 instead of psycopg2-binary

**Context:** Phase 0 — Python DB driver selection

**What happened:** Bob initially generated requirements.txt with `psycopg2-binary`. On Python 3.13 on Windows, there is no prebuilt binary wheel for psycopg2-binary (C extension compilation required).

**Decision:** Switch to `psycopg[binary]==3.3.4` (psycopg3), which has a prebuilt binary for Python 3.13. The SQLAlchemy session also needs a URL normalizer: `postgresql://` → `postgresql+psycopg://`.

**Rationale:** psycopg3 is the recommended modern driver and fully supported by SQLAlchemy 2.0. The additional complexity of the URL normalizer is worth it for reliable installation.

---

## Decision 2: Java Tests Verified Through Containerized Maven

**Context:** Java analytics verification

**What happened:** Maven (`mvn`) was not installed directly on the Windows PATH, and the production analytics container intentionally contains only the Java runtime, not Maven.

**Decision:** Run the Java test suite through a temporary Maven Docker container mounted to the analytics source directory. The repository also includes `mvnw` and `mvnw.cmd` for local development.

**Verification:** The complete Java analytics suite was executed successfully with 16 tests passing, 0 failures, and 0 errors.

**Rationale:** Using a containerized Maven environment provides reproducible verification without modifying the production runtime image or requiring a global Maven installation.

---

## Decision 3: Direct bcrypt Library instead of passlib

**Context:** Phase 2 — Password hashing

**What happened:** `passlib[bcrypt]` version 1.7.4 is incompatible with `bcrypt` version 5.0+ because passlib tries to access `bcrypt.__about__.__version__` which no longer exists. Tests failed with `ValueError: password cannot be longer than 72 bytes`.

**Decision:** Replace `passlib.context.CryptContext` with direct calls to the `bcrypt` library:
```python
bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
bcrypt.checkpw(plain.encode(), hashed.encode())
```

**Rationale:** The bcrypt library is the underlying implementation anyway. The direct API is simpler and avoids the passlib compatibility layer.

---

## Decision 4: SimpleNamespace for Test Users

**Context:** Phase 2 — Auth unit tests

**What happened:** `User.__new__(User)` creates a User instance without running `__init__`, but SQLAlchemy's mapper requires initialization. Setting attributes on an uninitialized ORM object raises `AttributeError: 'NoneType' object has no attribute 'set'`.

**Decision:** Use `types.SimpleNamespace` to create duck-typed user objects for tests. These objects have the same attributes as ORM users but no SQLAlchemy overhead.

**Rationale:** Unit tests should not depend on SQLAlchemy internals. SimpleNamespace objects are simpler, faster, and don't require a mapped class.

---

## Decision 5: Hand-Written Alembic Migration

**Context:** Phase 1 — Database migration

**What happened:** `alembic revision --autogenerate` requires a live database connection. PostgreSQL was not running locally.

**Decision:** Generate a blank revision with `alembic revision -m "initial_schema"` then hand-write the complete migration DDL.

**Rationale:** A hand-written migration is more explicit and fully reviewed. It's actually preferable in production to auto-generated migrations, which can include unwanted noise. The migration was later verified against a live PostgreSQL database: `alembic upgrade head` completed successfully, followed by successful execution of the demo seed script.

---

## Decision 6: PII Regex Ordering

**Context:** Phase 8 — PII masking

**What happened:** Applying `_PHONE_RE` before `_STUDENT_ID_RE` caused the phone pattern to consume `S1234567` (matching `S` + digits as a partial phone number). Two tests failed.

**Decision:** Apply masking in order: email → student_id → phone → name.

**Rationale:** More specific patterns (student IDs with prefix letters) should be masked before more general patterns (phone numbers that might partially match). This ordering produces deterministic results.

---

## Decision 7: Conservative Name Masking Regex

**Context:** Phase 8 — PII masking test correction

**What happened:** A test expected `"I'm Alice Johnson"` to be masked. The regex only handles `"My name is X"` / `"I am X"` prefix patterns. "I'm" is a contraction not covered.

**Decision:** Keep the conservative regex and correct the test to use the documented trigger phrase (`"My name is Alice Johnson"`).

**Rationale:** Academic text frequently uses proper nouns that are not names (course names, author names in citations, etc.). Overly aggressive name masking would corrupt legitimate academic content. The conservative approach minimizes false positives.

---

## Decision 8: Threshold Message Returns 200, Not 403

**Context:** Phase 7 — Analytics threshold enforcement

**What happened:** When an instructor requests analytics and the response threshold has not been met, the options are: return 403, 204, or a 200 with a threshold message.

**Decision:** Return 200 with a JSON body containing `message`, `totalSubmissions`, and `threshold`.

**Rationale:** A 403 implies the request is forbidden, which is confusing for the frontend (the instructor is authorized). The threshold is a data availability issue, not an authorization failure. A 200 with an informative message is cleaner and allows the frontend to display a user-friendly message with the actual counts.

---

## Decision 9: alembic.ini Default URL

**Context:** Phase 1 — Alembic configuration

**What happened:** The original `alembic.ini` used `%(DATABASE_URL)s` as a ConfigParser interpolation placeholder. This caused an `InterpolationMissingOptionError` when running `alembic` without the env var set.

**Decision:** Replace `%(DATABASE_URL)s` with a hardcoded localhost default in `alembic.ini`. The `env.py` still overrides from `DATABASE_URL` env var when present.

**Rationale:** ConfigParser `%()s` interpolation only works for keys defined within the ini file, not environment variables. The correct pattern is to set the config value in Python code (`config.set_main_option`), not in the ini file.

---

## Decision 10: No Refresh Tokens in MVP

**Context:** Phase 2 — Token lifetime

**What happened:** The plan specifies `REFRESH_TOKEN_EXPIRE_DAYS: int = 7` in config, suggesting refresh tokens were originally planned.

**Decision:** Implement only access tokens (60-minute expiry). Refresh token endpoint (`POST /api/v1/auth/refresh`) is not implemented in this MVP.

**Rationale:** Refresh tokens add significant complexity (token rotation, blacklisting, secure httpOnly cookies vs. localStorage). The 60-minute access token is acceptable for a university evaluation system where sessions are typically short. Refresh tokens are listed as explicit out-of-scope in the project plan.


---

## Decision 11: Aggregate CSV Reports Instead of Exporting Individual Responses

**Context:** Reports and privacy review

**What happened:** The Reports interface described CSV exports as aggregated statistics, but `CsvExportService` was generating one row per individual answer with a `submission_index`. Student identity was removed, but the report still exposed de-identified individual response patterns.

**Decision:** Replace the flat per-submission CSV format with one aggregated row per evaluation question. The export now contains question average, rating distribution from 1 to 5, and total response count.

**Rationale:** Aggregated reporting better matches the stated privacy model, reduces re-identification risk, and makes the exported report consistent with the analytics dashboard.

**Engineering improvement:** `CsvExportService` now reuses `CampaignStatsService` rather than duplicating analytics calculations.

**Verification:** A regression test was written first and initially failed against the old behavior. After the implementation change, all CSV tests passed and the complete Java suite passed with 16 tests, 0 failures, and 0 errors.

---

## Decision 12: Enforce the Minimum-Response Threshold on CSV Export

**Context:** Privacy and authorization review

**What happened:** Instructor analytics correctly hid results when the number of submissions was below `min_responses_threshold`, but the CSV export endpoint did not apply the same rule. An instructor could therefore request the CSV endpoint directly and bypass the privacy threshold.

**Decision:** Enforce the same campaign threshold in the CSV export API for instructor users. Administrators retain access for administrative review.

**Rationale:** Privacy controls must be enforced by the backend API at every data-access path, not only by the frontend or a single analytics endpoint.

**Verification:** A regression test was written before the fix. It initially failed because no `HTTPException` was raised for an instructor below the threshold. After the fix, both tests passed: instructors are blocked below the threshold and administrators retain access.


