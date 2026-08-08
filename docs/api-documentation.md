# API Documentation

## Authentication

### POST /api/v1/auth/login

Authenticate a user and receive a JWT access token.

**Request:**
```json
{
  "email": "admin@bobcourse.edu",
  "password": "Admin1234!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` — Invalid credentials

---

## User Profile

### GET /api/v1/me

Returns the authenticated user's profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": "uuid",
  "email": "student@bobcourse.edu",
  "full_name": "Alice Johnson",
  "role": "student",
  "department_id": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## Student Evaluation Flow

### GET /api/v1/me/enrollments

Returns enrolled courses with campaign status. **Student only.**

**Response (200):**
```json
[
  {
    "enrollment_id": "uuid",
    "course_offering_id": "uuid",
    "course_code": "CS101",
    "course_name": "Introduction to Computer Science",
    "section_number": "001",
    "semester_name": "Fall 2024",
    "instructor_name": "Dr. Jane Smith",
    "enrolled_at": "2024-09-01T00:00:00Z",
    "campaign": {
      "campaign_id": "uuid",
      "status": "open",
      "has_submitted": false
    }
  }
]
```

### GET /api/v1/evaluation-campaigns/{campaign_id}/questions

Returns questions for a campaign evaluation form.

**Response (200):**
```json
[
  {
    "id": "uuid",
    "template_id": "uuid",
    "text": "How would you rate the overall quality of this course?",
    "order_index": 0,
    "is_required": true
  }
]
```

### POST /api/v1/submissions

Submit an evaluation. **Student only.**

**Request:**
```json
{
  "campaign_id": "uuid",
  "answers": [
    { "question_id": "uuid", "rating": 4 },
    { "question_id": "uuid", "rating": 5 }
  ],
  "comment": "Excellent course! Highly recommend."
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "campaign_id": "uuid",
  "submitted_at": "2024-12-01T14:30:00Z"
}
```

**Errors:**
- `403` — Not enrolled or campaign not open
- `409` — Already submitted

---

## Analytics (Admin + Instructor)

### GET /api/v1/analytics/campaigns/{campaign_id}/stats

Returns campaign statistics proxied from Java. Instructors see threshold message if below minimum responses.

**Response (200) — admin or threshold met:**
```json
{
  "campaignId": "uuid",
  "courseCode": "CS101",
  "courseName": "Intro CS",
  "totalSubmissions": 18,
  "totalEnrolled": 25,
  "responseRate": 72.0,
  "overallAverage": 4.12,
  "questionStats": [
    {
      "questionId": "uuid",
      "questionText": "Overall quality?",
      "average": 4.2,
      "distribution": { "1": 0, "2": 1, "3": 2, "4": 8, "5": 7 }
    }
  ]
}
```

**Response (200) — instructor below threshold:**
```json
{
  "message": "Results not yet available. Minimum 5 responses required.",
  "totalSubmissions": 3,
  "threshold": 5
}
```

### GET /api/v1/analytics/dashboard

University-wide KPI dashboard.

**Response (200):**
```json
{
  "totalCampaigns": 12,
  "activeCampaigns": 4,
  "totalSubmissions": 234,
  "averageRating": 3.87,
  "overallResponseRate": 68.5
}
```

### GET /api/v1/analytics/campaigns/{campaign_id}/export-csv

Returns aggregated per-question statistics as a CSV file download. The export contains averages, rating distributions (1-5), and total response counts. It does not contain student_id, student email, submission indexes, or individual submission rows.

For instructors, CSV export is blocked with HTTP 403 when the campaign has not reached its configured minimum-response threshold. Administrators retain access for administrative review.

---

## AI Insights

### POST /api/v1/ai-insights/campaigns/{campaign_id}/trigger

Trigger AI analysis for a campaign. **Admin only.**

### GET /api/v1/ai-insights/campaigns/{campaign_id}

View AI insight for a campaign. **Admin + Instructor.**

**Response (200):**
```json
{
  "id": "uuid",
  "campaign_id": "uuid",
  "summary": "Analysis of 18 comments using keyword heuristics. Overall sentiment: positive.",
  "sentiment": "positive",
  "themes": ["Teaching", "Course Materials"],
  "improvement_areas": ["More Examples"],
  "provider_used": "offline_fallback",
  "generated_at": "2024-12-01T00:00:00Z",
  "human_reviewed": false,
  "disclaimer_acknowledged": false
}
```

### GET /api/v1/ai-insights/disclaimer

Returns the responsible AI disclaimer text.

### POST /api/v1/ai-insights/insights/{insight_id}/review

Mark an insight as human-reviewed. **Admin only.**

---

## Academic Structure (Admin write, All read)

All academic structure endpoints follow the same pattern:
- `GET /` — list all
- `GET /{id}` — get by ID
- `POST /` — create (admin)
- `PUT /{id}` — update (admin)
- `DELETE /{id}` — delete (admin)

Endpoints: `/api/v1/colleges`, `/api/v1/departments`, `/api/v1/courses`, `/api/v1/semesters`, `/api/v1/course-offerings`

---

## Admin — Users

- `GET /api/v1/users` — list all users
- `GET /api/v1/users/{id}` — get user
- `POST /api/v1/users` — create user
- `PUT /api/v1/users/{id}` — update user
- `DELETE /api/v1/users/{id}` — delete user

---

## Java Internal Endpoints (called by Python only)

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/internal/analytics/campaign-stats` | POST | Per-question stats |
| `/internal/analytics/course-trends` | POST | Multi-semester trends |
| `/internal/analytics/dashboard` | POST | University KPIs |
| `/internal/analytics/export-csv` | POST | CSV export |

These endpoints are never called directly by the frontend.


---

## Admin Dashboard Views

These read-only endpoints provide enriched data for the administrator dashboard.

### GET /api/v1/admin/stats

Returns university-wide administrator dashboard statistics.

**Access:** Admin only.

### GET /api/v1/admin/campaigns/overview

Returns evaluation campaigns enriched with course, semester, instructor, enrollment, submission, and campaign-status information.

**Access:** Admin only.

### GET /api/v1/admin/users

Returns an enriched user listing for the administrator dashboard.

**Access:** Admin only.

### GET /api/v1/admin/course-offerings/enriched

Returns course offerings enriched with course, semester, instructor, enrollment, and campaign information.

**Access:** Admin only.

