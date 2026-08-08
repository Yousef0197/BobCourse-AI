# BobCourse-AI UI Refresh Design

## Goal

Upgrade the existing frontend without changing the core backend architecture, database schema, or established API contracts.

## Visual Direction

Hybrid Academic AI:
- Dark navy sidebar/navigation
- Light content surfaces
- Emerald/teal primary accents
- Clean academic typography
- Professional SaaS-style cards, tables, forms, and status badges
- Minimal decorative effects; clarity takes priority

## Branding

Add a lightweight BobCourse AI visual identity and logo treatment that can be reused on:
- Login
- Navigation
- Dashboards

No external image dependency is required for the first implementation.

## Login Experience

Keep the existing authentication API unchanged.

Add three clearly labelled demo-account cards:
- Student Demo
- Instructor Demo
- Admin Demo

Selecting a card fills the existing email/password fields. The user still explicitly presses Sign In.

Display a small notice that demo credentials are for local/demo use only.

## Dashboard Improvements

Preserve all existing workflows and API calls.

Improve:
- Navigation hierarchy
- Page headers
- KPI cards
- Tables
- Forms
- Empty states
- Success/error messages
- Responsive spacing
- Status badges

## Small Functional Enhancements

1. Role-aware Quick Actions using existing routes.
2. Campaign progress / privacy-threshold indicator using data already returned by the backend.
3. Clear status guidance explaining the next available action for draft/open/closed/submitted states.

## Safety Constraints

- No database migration.
- No new backend service.
- No Java analytics architecture changes.
- No authentication contract changes.
- No untested major dependency upgrades.
- Existing role permissions must remain unchanged.
- Instructor privacy threshold remains enforced by the backend.
- Demo credentials must remain clearly identified as non-production.

## Verification

After each implementation group:
- npm run lint
- npm run build

Final verification:
- 69 Python tests
- 16 Java tests
- frontend lint
- frontend production build
