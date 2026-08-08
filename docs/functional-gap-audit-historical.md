> **Historical Audit Notice**
>
> This document captures an earlier functional-gap review performed during development.
> It does not represent the final state of BobCourse-AI.
> Many gaps listed below were subsequently resolved through implementation, end-to-end testing, privacy review, and human engineering judgment.
> Current implementation status is documented in `sdlc-evidence.md`, `testing-strategy.md`, `human-judgment.md`, and `bob-usage-report.md`.

---
# Functional Gap Audit — BobCourse-AI

**Date:** 2024-01  
**Auditor:** Software Engineer  
**Purpose:** Identify gaps between bootcamp requirements and the current implementation, then close them.

---

## Summary

The backend is substantially complete: 15 tables, full RBAC, JWT auth, Java analytics, and AI module all work. The primary gaps are in the **frontend** — the UI exposes only a fraction of the backend's capabilities and lacks real workflows. The backend also has minor gaps (VITE env prefix bug, thin seed data, missing course-trends route).

---

## Gap Table

| # | Requirement | Current Implementation | Gap | Required Change | Priority | Frontend | Python | Java | DB | Test |
|---|-------------|----------------------|-----|-----------------|----------|----------|--------|------|----|------|
| 1 | Admin can manage academic structure (CRUD) | Backend: full CRUD on colleges, depts, courses, semesters, offerings. Frontend: read-only lists | Frontend shows no create/edit controls | Add create/edit forms in AdminDashboard for each entity | P0 | Y | N | N | N | N |
| 2 | Admin can manage users | Backend: full CRUD at /api/v1/users. Frontend: not exposed | Users tab completely missing | Add Users section to AdminDashboard | P1 | Y | N | N | N | N |
| 3 | Admin can manage evaluation templates | Backend: full CRUD + questions. Frontend: not exposed | Templates tab missing | Add Templates page with question editor | P0 | Y | N | N | N | N |
| 4 | Admin can create campaigns linking offerings to templates | Backend: POST /evaluation-campaigns. Frontend: read-only table | No "Create Campaign" form | Add campaign creation form in AdminDashboard | P0 | Y | N | N | N | N |
| 5 | Admin can open/close campaigns | Backend: PUT /evaluation-campaigns/{id} with status. Frontend: no buttons | Status transitions not actionable | Add Open/Close buttons with confirmation | P0 | Y | N | N | N | N |
| 6 | Campaigns table shows course/semester context | Backend has data. Frontend shows only UUIDs | Campaigns show bare campaign_id with no context | Enrich campaigns view with course name, semester, instructor | P0 | Y | N | N | N | N |
| 7 | Instructor sees courses by name not UUID | Backend: instructor_id on offering; instructors listed by userId. Frontend filters offerings by userId but shows no course name | Course name/semester missing from instructor view | Resolve course/semester names in instructor dashboard | P0 | Y | N | N | N | N |
| 8 | Analytics shows per-campaign stats including course name | Backend: GET /analytics/campaigns/{id}/stats via Java. Frontend: shows stats but only for closed campaigns, no course context | Missing course/semester label on stats | Include course code/name from Java response | P1 | Y | N | N | N | N |
| 9 | CSV export accessible from UI | Backend: GET /analytics/campaigns/{id}/export-csv. Frontend: not exposed | No "Export CSV" button anywhere | Add Export CSV button on campaign stats view | P1 | Y | N | N | N | N |
| 10 | AI insights triggerable from campaigns view | Backend: POST /ai-insights/campaigns/{id}/trigger. Frontend: AIInsightsPanel only in analytics tab for closed campaigns | Cannot trigger from campaign management | Expose trigger on campaign detail/analytics | P1 | Y | N | N | N | N |
| 11 | Admin dashboard shows meaningful KPIs (students, instructors, etc.) | Backend: users and campaigns exist. Frontend: shows only colleges/depts/courses/semesters counts | No student count, instructor count, submission count | Add /api/v1/analytics/dashboard to dashboard + user counts | P0 | Y | N | N | N | N |
| 12 | Student sees success state after submission | Backend: 201 created. Frontend: navigates back to /student with { state: { submitted: true } } but does not use the state | Success state unused | Use navigate state to show success banner on return | P1 | Y | N | N | N | N |
| 13 | Instructor sees results for open campaigns too | Frontend: `enabled: campaign.status === 'closed'` only | Results only shown for closed campaigns, not open ones with submissions | Show stats once status is open and threshold is met | P1 | Y | N | N | N | N |
| 14 | Course-trends analytics endpoint | Backend: Python /analytics/campaigns/{id}/stats + Java trend computation. Python service.get_dashboard() exists but no trend call exposed | No trend endpoint in Python analytics router | Add GET /analytics/courses/{course_id}/trends to Python | P2 | Y | Y | N | N | Y |
| 15 | VITE_API_BASE_URL in docker-compose missing /api/v1 | docker-compose has `VITE_API_BASE_URL=http://localhost:8000` but apiClient.ts uses the full env var as baseURL | Login works (fixed externally) but this documents the known state | Document only — fix already applied by user | P0 | Y | N | N | N | N |
| 16 | Seed data demonstrates complete workflow | Seed: 1 student, 1 instructor, 1 course, draft campaign | No open campaigns, no synthetic submissions, no completed evaluations to show analytics | Enhance seed: add open campaign + second student + synthetic submissions | P0 | N | Y | N | N | N |
| 17 | Admin navigation is a flat 3-tab page | AdminDashboard uses 3 tabs: overview, campaigns, analytics | Professional navigation requires sidebar with multiple sections | Rebuild AdminDashboard as sidebar layout with 6+ sections | P0 | Y | N | N | N | N |
| 18 | Responsible AI: disclaimer must be visible prominently | AIInsightsPanel has disclaimer + checkbox gate | Accessible but only after navigating to analytics tab | Ensure visible whenever AI insights are accessed | P0 | Y | N | N | N | N |

---

## Implementation Actions (Prioritized)

### P0 (Implement First)
1. Fix docker-compose VITE env (document — already fixed by user)
2. Enhance seed data with open campaign + 2 more students + synthetic submissions
3. Rebuild AdminDashboard with sidebar navigation
4. Add campaign creation form with course offering + template selectors
5. Add Open/Close buttons with backend calls
6. Enrich campaign list with course/semester names
7. Add academic structure create/edit (colleges, departments, courses, semesters, offerings)
8. Fix instructor dashboard to resolve course/semester names
9. Add dashboard KPIs using /analytics/dashboard

### P1 (Implement Second)
10. Add Users management section
11. Add Templates management (create/edit with questions)
12. Add CSV Export button
13. Fix student success state
14. Show stats for open campaigns (not just closed)
15. Add AI insights trigger from campaign management

### P2 (If Time Permits)
16. Add course-trends Python endpoint and trend visualization

---

## Decisions

**D1: Campaign-list enrichment (Gap #6)** — The campaign response schema does not include course name/semester. Rather than adding a DB join to the campaign schema (which could expose privacy-sensitive data paths), a new enriched endpoint `GET /analytics/campaigns/overview` will be added that returns campaign list with course/semester context for admin only.

**D2: Instructor course resolution (Gap #7)** — The frontend currently filters offerings by userId but has no course/semester names. The `/course-offerings` endpoint returns only IDs. A new enriched GET endpoint `GET /course-offerings/my-courses` (instructor-only) will return offerings with resolved course and semester details. This is better than loading all courses/semesters separately.

**D3: No destructive deletes on academic structure** — Deleting a college/department/course that has historical evaluations would corrupt data. Frontend will show disable/deactivate controls rather than hard delete for any entity linked to campaigns. This is documented as a Human Engineering Judgment decision.

