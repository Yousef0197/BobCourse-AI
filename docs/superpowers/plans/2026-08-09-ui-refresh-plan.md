# BobCourse-AI UI Refresh Implementation Plan

**Goal:** Upgrade BobCourse-AI into a polished Hybrid Academic AI interface without changing backend contracts or database architecture.

**Tech Stack:** React 18, TypeScript, Vite, React Query, Axios.

## Global Constraints

- Preserve all existing API calls and role permissions.
- No database migrations.
- No new backend or Java service.
- No major dependency upgrades.
- Work only on the `ui-refresh` branch.
- Verify every implementation group with lint and production build.

---

## Task 1 — Shared Visual System + Branding

**Files:**
- Modify: `frontend/src/index.css`
- Create: `frontend/src/components/Brand.tsx`

**Deliverable:**
- Navy + emerald/teal design tokens.
- Reusable BobCourse AI logo/wordmark using CSS/HTML only.
- Shared buttons, cards, badges, form controls, page layout and responsive utilities.
- No external image dependency.

**Verification:**
- `npm run lint`
- `npm run build`

---

## Task 2 — Login + Demo Accounts

**Files:**
- Modify: `frontend/src/pages/LoginPage.tsx`
- Reuse: `frontend/src/components/Brand.tsx`

**Deliverable:**
- Premium split-layout login experience.
- Student Demo card.
- Instructor Demo card.
- Admin Demo card.
- Selecting a demo fills the existing login form.
- User still explicitly presses Sign In.
- Non-production demo notice.
- Existing authentication API remains unchanged.

**Verification:**
- Student credentials populate correctly.
- Instructor credentials populate correctly.
- Admin credentials populate correctly.
- Normal manual login still works.
- `npm run lint`
- `npm run build`

---

## Task 3 — Dashboard Visual Refresh

**Files:**
- Modify: `frontend/src/pages/StudentDashboard.tsx`
- Modify: `frontend/src/pages/InstructorDashboard.tsx`
- Modify: `frontend/src/pages/AdminDashboard.tsx`
- Modify: `frontend/src/components/AIInsightsPanel.tsx`

**Deliverable:**
- Consistent Hybrid Academic AI layout.
- Improved sidebar/header hierarchy.
- Professional KPI cards and tables.
- Clear status badges.
- Better empty/error/success states.
- Existing workflows and API calls preserved.

**Verification:**
- Student workflow remains functional.
- Instructor privacy state remains visible.
- Admin navigation remains functional.
- `npm run lint`
- `npm run build`

---

## Task 4 — Three Small UX Enhancements

**Deliverable:**

1. **Quick Actions**
   - Role-aware shortcuts to existing workflows.

2. **Campaign Progress**
   - Visual response/threshold progress using existing backend data.
   - Never bypass backend privacy enforcement.

3. **Next Action Guidance**
   - Clear guidance for draft/open/closed/submitted states.

**Verification:**
- No new backend contract required.
- Role permissions unchanged.
- `npm run lint`
- `npm run build`

---

## Final Verification

- Python: 69 tests pass.
- Java: 16 tests pass.
- Frontend ESLint: 0 errors / 0 warnings.
- Frontend production build succeeds.
- Manual login test for Student, Instructor and Admin.
- Manual check of the three dashboards.

Only after final verification should `ui-refresh` be merged into `master`.
