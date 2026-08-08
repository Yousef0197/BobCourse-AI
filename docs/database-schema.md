# Database Schema

## Entity Relationship Summary

```
colleges ──< departments ──< courses
semesters ──< course_offerings >── courses
                    │
              enrollments >── users (students)
                    │
         evaluation_campaigns ──── course_offerings
                    │
        evaluation_submissions ──< evaluation_answers
                    │               └── evaluation_questions
                    │
              text_comments ──── evaluation_submissions
                    │
               ai_insights ──── evaluation_campaigns

users >── roles (enum: student / instructor / admin)
departments >── users (instructor assignment)
audit_logs ──── users (actor)
```

## Tables (15 total)

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | |
| hashed_password | VARCHAR(255) | bcrypt cost=12 |
| full_name | VARCHAR(255) | |
| role | ENUM(student, instructor, admin) | |
| department_id | UUID FK → departments | nullable |
| is_active | BOOLEAN DEFAULT true | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### colleges
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(255) UNIQUE | |
| code | VARCHAR(20) UNIQUE | |
| created_at | TIMESTAMPTZ | |

### departments
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(255) | |
| code | VARCHAR(20) | |
| college_id | UUID FK → colleges | NOT NULL |
| created_at | TIMESTAMPTZ | |

### courses
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| code | VARCHAR(20) UNIQUE | |
| name | VARCHAR(255) | |
| credit_hours | INTEGER | |
| department_id | UUID FK → departments | |
| created_at | TIMESTAMPTZ | |

### semesters
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(100) | e.g. "Fall 2024" |
| season | ENUM(fall, spring, summer) | |
| year | INTEGER | |
| start_date | DATE | |
| end_date | DATE | |
| is_active | BOOLEAN DEFAULT false | only one active at a time |

### course_offerings
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| course_id | UUID FK → courses | |
| semester_id | UUID FK → semesters | |
| instructor_id | UUID FK → users | role=instructor enforced |
| section_number | VARCHAR(20) | |
| capacity | INTEGER | |
| UNIQUE | (course_id, semester_id, section_number) | |

### enrollments
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| student_id | UUID FK → users | role=student enforced |
| course_offering_id | UUID FK → course_offerings | |
| enrolled_at | TIMESTAMPTZ | |
| UNIQUE | (student_id, course_offering_id) | prevents duplicates |

### evaluation_templates
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(255) | |
| description | TEXT | nullable |
| is_active | BOOLEAN DEFAULT true | |
| created_by | UUID FK → users | admin only |
| created_at | TIMESTAMPTZ | |

### evaluation_questions
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| template_id | UUID FK → evaluation_templates | |
| text | TEXT | |
| order_index | INTEGER | display order |
| is_required | BOOLEAN DEFAULT true | |
| UNIQUE | (template_id, order_index) | |

### evaluation_campaigns
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| course_offering_id | UUID FK → course_offerings | UNIQUE — one campaign per offering |
| template_id | UUID FK → evaluation_templates | |
| status | ENUM(draft, open, closed) DEFAULT draft | |
| opens_at | TIMESTAMPTZ | nullable |
| closes_at | TIMESTAMPTZ | nullable |
| min_responses_threshold | INTEGER DEFAULT 5 | before instructor can see results |
| created_by | UUID FK → users | |
| created_at | TIMESTAMPTZ | |

### evaluation_submissions
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| campaign_id | UUID FK → evaluation_campaigns | |
| student_id | UUID FK → users | **anonymity note: used for constraint only** |
| submitted_at | TIMESTAMPTZ | |
| UNIQUE | (campaign_id, student_id) | one submission per student per campaign |

### evaluation_answers
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| submission_id | UUID FK → evaluation_submissions | |
| question_id | UUID FK → evaluation_questions | |
| rating | INTEGER | CHECK 1 ≤ rating ≤ 5 |
| UNIQUE | (submission_id, question_id) | |

### text_comments
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| submission_id | UUID FK → evaluation_submissions | UNIQUE — one comment per submission |
| content | TEXT | max 2000 chars |
| is_flagged | BOOLEAN DEFAULT false | PII flag from AI analysis |

### ai_insights
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| campaign_id | UUID FK → evaluation_campaigns | UNIQUE |
| summary | TEXT | nullable |
| sentiment | ENUM(positive, neutral, negative, mixed) | nullable |
| themes | JSONB | list of strings |
| improvement_areas | JSONB | list of strings |
| provider_used | VARCHAR(100) | "offline_fallback" or "openai" |
| generated_at | TIMESTAMPTZ | |
| human_reviewed | BOOLEAN DEFAULT false | |
| reviewed_by | UUID FK → users | admin who reviewed |
| reviewed_at | TIMESTAMPTZ | |
| disclaimer_acknowledged | BOOLEAN DEFAULT false | |

### audit_logs
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| actor_id | UUID FK → users | nullable (system events) |
| action | VARCHAR(100) | e.g. "campaign.opened" |
| resource_type | VARCHAR(100) | e.g. "evaluation_campaign" |
| resource_id | UUID | nullable |
| details | JSONB | additional context |
| ip_address | INET | nullable |
| occurred_at | TIMESTAMPTZ | |

## Anonymity Architecture

`evaluation_submissions.student_id` is stored for two purposes only:
1. Enforcing the one-submission-per-student UNIQUE constraint
2. Admin abuse investigation (access-controlled)

The `student_id` is **never returned** by instructor-facing API endpoints. The Java analytics service **never receives** `student_id`. `text_comments` has no student reference — it links only to `submission_id`, which is opaque to instructors.

## Migration

The initial migration (`alembic/versions/8dd7820bb9d1_initial_schema.py`) creates all 15 tables, 4 ENUMs, constraints, and indexes.

Run: `alembic upgrade head`

