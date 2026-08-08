# Technical Documentation

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Container runtime |
| Docker Compose | 2.x | Multi-service orchestration |
| Python | 3.11–3.13 | Core service local dev |
| Java | 17+ | Analytics service local dev |
| Maven | 3.8+ | Java build (or use ./mvnw) |
| Node.js | 18+ | Frontend local dev |
| npm | 9+ | Frontend package manager |

## Environment Configuration

Copy `.env.example` to `.env` and set the required variables:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | CHANGE_ME | JWT signing secret — **must change in production** |
| `DATABASE_URL` | postgresql://bobcourse:bobcourse@localhost:5432/bobcourse_db | PostgreSQL connection string |
| `ANALYTICS_SERVICE_URL` | http://localhost:8080 | Java analytics service URL |
| `AI_PROVIDER` | offline | AI provider: "offline" or "openai" |
| `OPENAI_API_KEY` | (empty) | OpenAI API key (optional) |
| `MIN_RESPONSES_THRESHOLD` | 5 | Default minimum-response threshold; each campaign can configure its own value |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | JWT access token lifetime |
| `ALLOWED_ORIGINS` | http://localhost:5173 | CORS allowed origins |
| `APP_ENV` | development | Application environment |

## Docker Compose Services

```yaml
services:
  postgres:    # PostgreSQL 16
  core:        # Python FastAPI on port 8000
  analytics:   # Java Spring Boot on port 8080
  frontend:    # React + Vite dev server on port 5173
```

### Start all services

```bash
docker compose up --build
```

### Start just the database

```bash
docker compose up -d postgres
```

### Stop all services

```bash
docker compose down
```

### Reset database

```bash
docker compose down -v  # removes volumes including DB data
docker compose up --build
```

## Database Setup

### Apply migrations

```bash
cd backend/core
alembic upgrade head
```

### Seed demo data

```bash
cd backend/core
python -m app.db.seed
```

This creates:
- Admin user: `admin@bobcourse.edu` / `Admin1234!`
- Instructor user: `instructor@bobcourse.edu` / `Instructor1234!`
- Student user: `student@bobcourse.edu` / `Student1234!`
- College of Engineering → Computer Science department
- CS101 course, Fall 2024 semester, one course offering, one enrollment
- Evaluation template with 5 questions, draft campaign

### Check migration status

```bash
cd backend/core
alembic current
alembic history
```

## Python Service

### Local dev server (requires DB running)

```bash
cd backend/core
uvicorn app.main:app --reload --port 8000
```

### API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Java Analytics Service

### Local dev server

```bash
cd backend/analytics
./mvnw spring-boot:run
# or with Maven:
mvn spring-boot:run
```

### Build JAR

```bash
cd backend/analytics
./mvnw package -DskipTests
java -jar target/analytics-0.1.0.jar
```

## Frontend

### Development

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Production build

```bash
cd frontend
npm run build
# Output in frontend/dist/
```

### TypeScript check

```bash
cd frontend
npx tsc --noEmit
```

## Deployment Notes

### Production security checklist

- [ ] Change `SECRET_KEY` to a cryptographically random value (e.g., `openssl rand -hex 32`)
- [ ] Set `APP_ENV=production`
- [ ] Use HTTPS with a valid TLS certificate
- [ ] Configure `ALLOWED_ORIGINS` to the production frontend domain
- [ ] Use a managed PostgreSQL service with automated backups
- [ ] Set strong DB credentials (not the defaults)
- [ ] Restrict Java analytics service to internal network only (not exposed publicly)
- [ ] If using OpenAI: set `OPENAI_API_KEY` as a secret, not in `.env` file

### Java analytics service security

The Java service has no authentication — it trusts all callers. In production, this service should be:
- Not exposed to the public internet
- Accessible only from the Python service (network isolation via Docker/Kubernetes)
- Optionally: add a shared secret header check

## Troubleshooting

### `psycopg.errors.ConnectionTimeout`
PostgreSQL is not running. Start it: `docker compose up -d postgres`

### `alembic.errors.InterpolationMissingOptionError`
Old `alembic.ini` with `%(DATABASE_URL)s`. Fixed by replacing with literal URL.

### `bcrypt ValueError: password cannot be longer than 72 bytes`
passlib 1.7.4 + bcrypt 5.0 incompatibility. Fixed by using `bcrypt` library directly (see `app/core/security.py`).

### TypeScript error: `declared but never read`
Remove the unused variable. The ESLint config enforces `--max-warnings 0`.

### Java tests not running locally
Use `./mvnw test` (Maven Wrapper). If `mvn` is not on PATH, the wrapper downloads Maven automatically.




