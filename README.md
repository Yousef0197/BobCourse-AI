# BobCourse-AI — University Course Evaluation System

A full-stack university course evaluation system built with React + TypeScript, Python FastAPI, and Java Spring Boot.

## Architecture

```
React (Vite + TS)
      ↓ JWT auth
Python FastAPI (core)
      ↓ httpx (no student_id)
Java Spring Boot (analytics)
      ↑ pure computation, no DB
Python FastAPI ← PostgreSQL (exclusive)
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for local backend development)
- Java 17+ (for analytics service development)

### Run with Docker Compose

```bash
cp .env.example .env
# Edit .env — set a strong SECRET_KEY
docker compose up --build
```

| Service      | URL                       |
|-------------|--------------------------|
| Frontend     | http://localhost:5173      |
| Python API   | http://localhost:8000      |
| Java service | http://localhost:8080      |
| PostgreSQL   | localhost:5432             |
| API docs     | http://localhost:8000/docs |

### Demo Credentials

| Role       | Email                        | Password         |
|-----------|------------------------------|------------------|
| Admin      | admin@bobcourse.edu          | Admin1234!       |
| Instructor | instructor@bobcourse.edu     | Instructor1234!  |
| Student    | student@bobcourse.edu        | Student1234!     |

> ⚠ These are for demonstration only. Never use these passwords in production.

## Local Development

### Python Backend

```bash
cd backend/core
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Run tests
python -m pytest --tb=short -v
# Start dev server (requires PostgreSQL running)
uvicorn app.main:app --reload
```

### Seed the database

```bash
cd backend/core
python -m app.db.seed
```

### Alembic migrations

```bash
cd backend/core
# Apply migrations
alembic upgrade head
# Generate new migration after model change
alembic revision --autogenerate -m "description"
```

### Java Analytics Service

```bash
cd backend/analytics
./mvnw spring-boot:run   # or: mvn spring-boot:run
./mvnw test              # run tests
```

> Maven is not required locally if using `./mvnw` (Maven Wrapper).

### Frontend

```bash
cd frontend
npm install
npm run dev      # development server
npx tsc --noEmit # type check
npm run build    # production build
```

## Project Structure

```
BobCourse-AI/
├── backend/
│   ├── core/               # Python FastAPI service
│   │   ├── app/
│   │   │   ├── api/        # Route handlers
│   │   │   ├── ai/         # Responsible AI module
│   │   │   ├── core/       # Config, JWT, deps, security
│   │   │   ├── db/         # Base, session, seed
│   │   │   ├── models/     # SQLAlchemy ORM (15 tables)
│   │   │   ├── schemas/    # Pydantic schemas
│   │   │   └── services/   # Business logic
│   │   ├── alembic/        # DB migrations
│   │   └── tests/          # pytest test suite
│   └── analytics/          # Java Spring Boot service
│       └── src/
│           ├── main/java/  # DTOs, services, controllers
│           └── test/java/  # JUnit 5 tests
├── frontend/               # React + Vite + TypeScript
│   └── src/
│       ├── components/     # Shared components
│       ├── lib/            # apiClient, auth helpers
│       └── pages/          # Login, dashboards, forms
├── docs/                   # All documentation
├── docker-compose.yml
├── .env.example
└── .github/workflows/ci.yml
```

## Running Tests

Verified results:

- Python Core: **69 passed**
- Java Analytics: **16 passed**
- Total automated tests: **85 passed**
- Frontend ESLint: **0 errors, 0 warnings**
- Frontend production build: **successful**

```bash
# Python (no DB required)
cd backend/core && python -m pytest --tb=short -v

# Java (requires Maven)
cd backend/analytics && ./mvnw test

# Frontend TypeScript check
cd frontend && npx tsc --noEmit

# Frontend production build
cd frontend && npm run build
```

## Security

- All passwords hashed with bcrypt (cost factor 12)
- JWT HS256 tokens, 60-minute expiry
- Role-based access control on every protected endpoint
- student_id never returned to instructor-facing endpoints
- student_id never sent to Java analytics service
- Configurable minimum-response threshold before instructors can view analytics or export CSV reports
- CSV reports contain aggregated statistics only, with no individual submission indexes
- PII masking before any AI analysis

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design and component interactions |
| [Database Schema](docs/database-schema.md) | All 15 tables with relationships |
| [API Documentation](docs/api-documentation.md) | All endpoints with request/response |
| [Security](docs/security.md) | Security model and RBAC |
| [Responsible AI](docs/responsible-ai.md) | AI principles, PII protection, offline fallback |
| [Bob Usage Report](docs/bob-usage-report.md) | How IBM Bob was used in this project |
| [Human Judgment](docs/human-judgment.md) | Engineering decisions and rationale |
| [SDLC Evidence](docs/sdlc-evidence.md) | Phase-by-phase development evidence |
| [Testing Strategy](docs/testing-strategy.md) | Test approach and coverage |
| [Technical Documentation](docs/technical-documentation.md) | Setup, deployment, configuration |


