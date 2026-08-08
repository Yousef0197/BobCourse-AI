# Architecture

## System Overview

BobCourse-AI is a three-tier web application for university course evaluation.

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│         (Vite + TypeScript + React Query + Axios)        │
│  Login │ Student Dashboard │ Instructor Dashboard │ Admin│
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS / JWT Bearer
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Python FastAPI (Core Service)               │
│  Auth │ CRUD │ Submissions │ Analytics Proxy │ AI Module │
│                      │                                   │
│                 ┌────┴────┐                              │
│                 │PostgreSQL│  (exclusively owned)        │
│                 └─────────┘                              │
└──────────────────────┬──────────────────────────────────┘
                       │ httpx POST (no student_id)
                       ▼
┌─────────────────────────────────────────────────────────┐
│           Java Spring Boot (Analytics Service)           │
│  CampaignStats │ Trends │ Dashboard │ CSV Export          │
│  Pure computation — no DB access, no student_id         │
└─────────────────────────────────────────────────────────┘
```

## Key Architecture Decisions

### 1. Java Has No DB Access
Java receives data payloads from Python and performs pure statistical computation. This means:
- Python owns all data — Java cannot bypass security rules
- student_id is stripped by Python before sending to Java
- Java is stateless and easily testable with known inputs

### 2. Frontend Never Calls Java Directly
All analytics requests go through Python, which:
- Authenticates and authorizes the request
- Fetches data from PostgreSQL
- Strips student_id
- Calls Java with the anonymized payload
- Returns the Java result to the frontend

### 3. Anonymity Architecture
`evaluation_submissions` stores `student_id` for two purposes only:
1. Enforcing the one-submission-per-student constraint (database UNIQUE index)
2. Admin abuse investigation (access-controlled, never exposed in analytics)

The `text_comments` table has no student reference — it links only to `submission_id`.

### 4. Responsible AI
- PII masking before any AI analysis
- Offline fallback provider requires no external API key
- OpenAI provider is guarded by `OPENAI_API_KEY` env var
- All AI outputs carry a mandatory disclaimer
- Human review flag on every insight

## Technology Stack

| Layer         | Technology                      | Version |
|--------------|--------------------------------|---------|
| Frontend      | React + TypeScript + Vite       | 18.3 / 5.5 |
| State Mgmt    | TanStack React Query            | 5.x     |
| HTTP Client   | Axios                           | 1.7     |
| Router        | React Router DOM                | 6.x     |
| Python        | FastAPI + Uvicorn               | 0.111 / 0.30 |
| ORM           | SQLAlchemy                      | 2.0     |
| Migrations    | Alembic                         | 1.13    |
| DB Driver     | psycopg (psycopg3)              | 3.3     |
| Auth          | python-jose (JWT) + bcrypt      | 3.3 / 5.0 |
| HTTP Client   | httpx                           | 0.27    |
| Java          | Spring Boot                     | 3.3     |
| Java Build    | Maven                           | 3.x     |
| Database      | PostgreSQL                      | 15+     |
| Container     | Docker + Docker Compose         | latest  |
| CI/CD         | GitHub Actions                  | latest  |

## API Design

### Python FastAPI Route Groups

| Prefix | Role Access | Purpose |
|--------|-------------|---------|
| `/api/v1/auth` | All | Login |
| `/api/v1/me` | All | Own profile, enrollments |
| `/api/v1/users` | Admin | CRUD users |
| `/api/v1/colleges` | Admin write, all read | Academic structure |
| `/api/v1/departments` | Admin write, all read | Academic structure |
| `/api/v1/courses` | Admin write, all read | Course catalog |
| `/api/v1/semesters` | Admin write, all read | Semester management |
| `/api/v1/course-offerings` | Admin write, all read | Offering management |
| `/api/v1/enrollments` | Admin write | Enrollment management |
| `/api/v1/evaluation-templates` | Admin write, all read | Templates |
| `/api/v1/evaluation-campaigns` | Admin write, all read | Campaign lifecycle |
| `/api/v1/submissions` | Student write | Submit evaluation |
| `/api/v1/analytics` | Admin + Instructor | Proxied from Java |
| `/api/v1/ai-insights` | Admin + Instructor | AI analysis |

### Java Spring Boot Internal Endpoints

| Endpoint | Purpose |
|---------|---------|
| `POST /internal/analytics/campaign-stats` | Per-question averages, distributions |
| `POST /internal/analytics/course-trends` | Multi-semester trend data |
| `POST /internal/analytics/dashboard` | University-wide KPIs |
| `POST /internal/analytics/export-csv` | Flat CSV generation |


