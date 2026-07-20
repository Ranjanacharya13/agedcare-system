# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend for an aged-care record-keeping system, backed by Supabase (Postgres), plus a React admin/public frontend (`frontend/`). The backend manages residents (with cognitive/disability classification) and employees, a large set of "child" record types scoped to each (medications, behaviour charts, qualifications, registrations, incidents, shifts, payroll, etc.), two standalone resources (complaints, appointments), and two read-only computed endpoints (resident risk scoring, shift-coverage suggestions). The frontend has a public landing page (appointment request form) at `/` and an internal staff app at `/admin/*`.

## Commands

Backend uses `uv` for dependency management (`uv.lock` present) and targets Python 3.13. Frontend uses `npm` (Vite + React, plain JS, no TypeScript).

```bash
# backend: install dependencies
uv sync

# backend: run the dev server (from repo root, defaults to :8000)
uv run fastapi dev backend/main.py

# backend: run all tests
uv run pytest

# backend: run a single test
uv run pytest backend/tests/test_health.py::test_health_check

# frontend: install dependencies (from frontend/)
npm install

# frontend: run the dev server (defaults to :5173)
npm run dev

# frontend: production build
npm run build
```

Environment variables are loaded from `backend/.env` (see `Settings` in `backend/config/settings.py`): `supabase_url`, `supabase_key`, `secret_key`, `access_token_expire_minutes`. A Supabase project with the corresponding tables must exist for anything beyond the health check to work — repository calls hit Supabase directly with no local DB fallback. Frontend config is `frontend/.env` (`VITE_API_BASE_URL`, defaults to `http://localhost:8000/api/v1`).

`backend/main.py` has `CORSMiddleware` allowing `localhost:5173`/`127.0.0.1:5173` (the Vite dev origin) — update this if the frontend is ever deployed elsewhere. There is no auth anywhere in this stack (see Auth below), so `/admin/*` on the frontend is a URL path, not an access boundary.

## Architecture

Layering is strict and consistent across every resource: **endpoint (router) → service → repository → Supabase table**. When adding a new resource, follow the existing pattern rather than inventing a new shape.

### Kinds of resources

1. **Top-level resources** (`residents`, `employees`) have their own dedicated model/schema/service/repository/endpoint files (e.g. `backend/services/resident_service.py`, `backend/repositories/resident_repository.py`, `backend/api/v1/endpoints/residents.py`). These are hand-written CRUD stacks with no parent concept.

2. **Parent-scoped "child" resources** — the majority of tables — are generic and built through shared infrastructure instead of per-resource files:
   - `backend/repositories/base.py` (`SupabaseRepository`) — generic CRUD against any Supabase table for a given Pydantic model.
   - `backend/services/base.py` (`ParentScopedService`) — wraps a repository plus a parent repository (residents or employees), enforcing that the parent exists and that child records belong to the given parent. Bumps `updated_at` on PATCH automatically when the model has that field.
   - `backend/api/v1/parent_scoped_router.py` (`build_parent_scoped_routers`) — generates two `APIRouter`s per resource: one nested under the parent (`/residents/{resident_id}/{slug}`) and one flat "list all" router (`/{slug}`). **The flat router only registers `GET`** — there is no create/update/delete on the flat path, only under the nested parent path.
   - `backend/api/deps.py` (`_make_scoped_service_getter`) — factory that wires a table name + model + FastAPI dependency together into a `get_..._service` function.
   - `backend/api/v1/router.py` — declares each resource once as a tuple in `_RESIDENT_RESOURCES` or `_EMPLOYEE_RESOURCES` (slug, Create/Update/Out schemas, service getter), then loops over the lists to mount both routers with the right prefix and tags.

   **To add a new resident- or employee-scoped resource**: create the Pydantic model (`backend/models/`) and Create/Update/Out schemas (`backend/schemas/`), add a `get_<x>_service` entry in `deps.py` via `_make_scoped_service_getter`, then add one tuple to `_RESIDENT_RESOURCES` or `_EMPLOYEE_RESOURCES` in `router.py`. No new router, service, or repository code is needed.

   The one exception is `medical_history`, which has bespoke service/repository files (`medical_history_service.py`, `medical_history_repository.py`) instead of using the generic `SupabaseRepository`/`ParentScopedService`, but still exposes both a parent-scoped router and an all-router the same way.

3. **Standalone bespoke resources** (`complaints` → `complaints_feedback` table, `appointments`) have no required parent — optional `resident_id`/`employee_id` links (complaints) or none at all (appointments, a public-submittable enquiry with no resident/employee link by design). Each mirrors the `residents`/`employees` hand-written stack exactly: own model/schema/repository/service/endpoint files, single flat router (no nesting), full CRUD. `AppointmentCreate` only accepts the publicly-submittable fields (name/email/phone/type/preferred date-time/message) — `status`/`scheduled_at`/`handled_by`/`admin_notes` are admin-only, settable only via `AppointmentUpdate`.

4. **Computed, read-only resources** (`risk-scores`, `shift-suggestions`) have no table and no create/update/delete — just a `GET` that computes a response from other tables on the fly:
   - `backend/services/risk_scoring.py` (`RiskScoringService`) — a weighted-sum scoring algorithm over a resident's cognitive status, fall-risk level, recent incidents, assistance level, and behaviour frequency. Weights are hand-picked constants, not learned. `GET /risk-scores` and `GET /residents/{id}/risk-score`.
   - `backend/services/shift_matching.py` (`ShiftMatchingService`) + `backend/services/employee_care_load.py` — a greedy algorithm suggesting which employees could cover a shift, ranked by (no conflict, lowest recent "care load" — the risk-weighted residents they've recently attended to, derived from `assessed_by`/`reported_by`/`recorded_by`/`updated_by` columns on the resident signal tables since there's no real employee↔resident assignment table). `GET /shifts/{id}/suggested-employees`.
   - Both parallelize their independent Supabase lookups with `asyncio.gather` rather than awaiting sequentially — this matters here specifically because each computation is several round-trips deep (score a resident → 4 queries; suggest coverage → per-candidate conflict/hours/care-load, each of which scores every recently-touched resident).

### Supabase access

- A single `AsyncClient` is created on startup (`backend/main.py` lifespan → `backend/db/supabase_client.py`) and fetched per-request via `get_supabase()`. There is no connection pooling logic to manage — Supabase's client handles it.
- Repositories talk to Supabase's `.table(...).select/insert/update/delete()` query builder directly; there is no ORM layer or migrations directory in this repo — schema changes happen in Supabase itself.
- Models generally carry `created_at`/`updated_at` and are dumped with `mode="json"` before insert/update so `date`/`datetime`/`UUID`/enum values serialize correctly for Supabase.

### Auth

`backend/config/security.py` has password hashing (`passlib`/bcrypt) and JWT creation (`pyjwt`) helpers, but no auth endpoints or dependency currently wire them into the API — treat this as scaffolding, not an enforced auth flow.

## Frontend (`frontend/`)

Vite + React 18, plain JavaScript/JSX (no TypeScript), `react-router-dom`, plain CSS with custom properties (no Tailwind/UI kit), native `fetch()` (no axios) — deliberately minimal dependencies throughout.

### Routing split

`frontend/src/App.jsx`: `/` is the public landing page (`pages/PublicLandingPage.jsx`, no sidebar) — a one-shot appointment-request form, not built on the admin resource machinery. Everything else lives under `/admin/*`, wrapped in `AppShell` (sidebar nav) and `DirectoryProvider` (loads the full residents/employees lists once for name lookups and `ReferenceSelect` dropdowns) — **both are scoped to the `/admin` route tree only**, not mounted globally, so the public page never fetches admin data.

### The core pattern: one generic `ResourcePanel`, driven by config

Mirrors the backend's own generic parent-scoped-resource philosophy. Instead of a hand-written page per resource, every admin CRUD screen is `<ResourcePanel resource={someConfig} parentId={optional} />`:
- `components/resource/ResourcePanel.jsx` / `ResourceTable.jsx` / `ResourceForm.jsx` — generic list + create/edit modal + delete, driven entirely by a config object.
- `config/*.config.js` — one config per resource (`residents.config.js`, `employees.config.js`, `complaints.config.js`, `appointments.config.js`, `residentResourceConfigs.js`, `employeeResourceConfigs.js`). Each field declares `type` (`text`/`textarea`/`number`/`date`/`time`/`datetime`/`boolean`/`enum`/`reference`/`group`), `required`, `editOnly` (admin-only fields hidden on create — e.g. appointment `status`/`admin_notes`), and for `reference` fields, what they point at.
- `config/enums.js` — every backend `StrEnum`'s literal values, must byte-match exactly (a mismatch is a silent 422, not a frontend error).
- **To add a new admin-manageable resource**: add a config object + a one-line `<ResourcePanel resource={...} />` page. No new table/form component needed.

Three reference shapes exist (`components/common/ReferenceSelect.jsx`): global lookup (`residents`/`employees`, backed by `DirectoryContext`), parent-scoped (`time_entries.shift_id`, looks up the current employee's own shifts), and plain free text that merely looks like a reference (`medications.prescribed_by`) — reference-ness is always an explicit config flag, never inferred from the field name.

The public landing page reuses `appointmentsConfig` (filtering out `editOnly` fields) for its form fields, so the public and admin forms can't drift out of sync, but does **not** use `ResourcePanel` — a visitor needs a one-shot form with a success state, not a data table.

### Design system

`styles/tokens.css` — two-tone brand (teal primary + coral secondary, both with gradient variants) for the UI shell, plus a separate 5-tone semantic set (neutral/info/success/warning/danger) used only for status badges via `config/badgeTones.js` (maps each enum literal to a tone — forcing every status into two brand hues would make badges unreadable). `components/layout/Icons.jsx` is a small hand-drawn inline SVG icon set (no icon library).
