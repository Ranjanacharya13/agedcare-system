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

# backend: print the AHP derivation of the risk weights + consistency ratio
uv run python -m backend.scripts.show_risk_weights

# frontend: install dependencies (from frontend/)
npm install

# frontend: run the dev server (defaults to :5173)
npm run dev

# frontend: production build
npm run build
```

Environment variables are loaded from `backend/.env` (see `Settings` in `backend/config/settings.py`): `supabase_url`, `supabase_key`, `secret_key`, `access_token_expire_minutes`, `cors_origins`, `public_form_rate_limit`, `public_form_rate_window_seconds`. **`secret_key` must be set to a real random value** — it signs access tokens, and the app logs a warning at startup while it is still `change-me`. A Supabase project with the corresponding tables must exist for anything beyond the health check to work — repository calls hit Supabase directly with no local DB fallback. Frontend config is `frontend/.env` (`VITE_API_BASE_URL`, defaults to `http://localhost:8000/api/v1`).

`backend/main.py` has `CORSMiddleware` reading its allowed origins from the `cors_origins` setting (defaults to the Vite dev origins) — set it in `.env` if the frontend is deployed elsewhere.

The database schema must exist before anything beyond `/health` works. Run `backend/sql/000_schema.sql` once in the Supabase SQL editor — it creates all 27 tables and is safe to run against a database that already has some of them. Then create the first account:

```bash
uv run python -m backend.scripts.create_admin
```

There is no self-registration endpoint by design — accounts are issued.

## Architecture

Layering is strict and consistent across every resource: **endpoint (router) → service → repository → Supabase table**. When adding a new resource, follow the existing pattern rather than inventing a new shape.

### Kinds of resources

1. **Top-level resources** (`residents`, `employees`) have their own endpoint files but share `CrudService` (`services/base.py`) and thin `SupabaseRepository` subclasses (`repositories/resident_repository.py` etc.). No parent concept.

2. **Parent-scoped "child" resources** — the majority of tables — are generic and built through shared infrastructure instead of per-resource files:
   - `backend/repositories/base.py` (`SupabaseRepository`) — generic CRUD against any Supabase table for a given Pydantic model.
   - `backend/services/base.py` (`ParentScopedService`) — wraps a repository plus a parent repository (residents or employees), enforcing that the parent exists and that child records belong to the given parent. Bumps `updated_at` on PATCH automatically when the model has that field.
   - `backend/api/v1/parent_scoped_router.py` (`build_parent_scoped_routers`) — generates two `APIRouter`s per resource: one nested under the parent (`/residents/{resident_id}/{slug}`) and one flat "list all" router (`/{slug}`). **The flat router only registers `GET`** — there is no create/update/delete on the flat path, only under the nested parent path.
   - `backend/api/deps.py` (`_make_scoped_service_getter`) — factory that wires a table name + model + FastAPI dependency together into a `get_..._service` function.
   - `backend/api/v1/router.py` — declares each resource once as a tuple in `_RESIDENT_RESOURCES` or `_EMPLOYEE_RESOURCES` (slug, Create/Update/Out schemas, service getter), then loops over the lists to mount both routers with the right prefix and tags.

   **To add a new resident- or employee-scoped resource**: create the Pydantic model (`backend/models/`) and Create/Update/Out schemas (`backend/schemas/`), add a `get_<x>_service` entry in `deps.py` via `_make_scoped_service_getter`, then add one tuple to `_RESIDENT_RESOURCES` or `_EMPLOYEE_RESOURCES` in `router.py`. No new router, service, or repository code is needed.

   `medical_history` follows the same pattern as every other child resource.

3. **The link resource** (`resident_assignments`) is the one many-to-many table: which employees care for which residents, as primary / secondary / relief key workers with a date range. It does not fit the parent-scoped pattern because it has to be readable from *both* ends, so it has its own repository (`resident_assignment_repository.py`, with `list_for_resident` and `list_for_employee`) and service (`assignment_service.py`).

   Editing is resident-scoped — `/residents/{id}/assignments` — because you add a carer *to* a resident. Reading has three enriched, read-only views that resolve names, live shift state and risk scores server-side rather than making the browser fan out a lookup per row:
   - `GET /residents/{id}/care-team` — who cares for this resident, who is on shift right now, whether a primary exists at all.
   - `GET /employees/{id}/caseload` — their residents ordered by risk, plus total risk load and weekly hours.
   - `GET /coverage` — facility-wide gaps: residents with no named primary (highest risk first), staff carrying nobody.

   Two invariants are enforced in both `AssignmentService` and the database (partial unique indexes in `000_schema.sql`): **one active primary carer per resident**, and **no duplicate employee on the same resident**. Assignments are closed with `end_date` rather than deleted, so "who was responsible for this resident in March" stays answerable — which matters when something goes wrong and an assessor asks.

   A third rule is enforced in the service layer (`ensure_can_care` in `assignment_service.py`): **only care roles (`CARING_ROLES` in `models/employee.py`: Registered Nurse, Care Planner, Care Coordinator) can be assigned**. Managers, administrators, kitchen and laundry staff are refused with a 422, and `carer_matching.py` drops them before ranking instead of only ranking them last.

   **Hourly care schedule** (`care-visits` → `resident_care_visits`): the day-to-day layer under the standing care team — this carer is with this resident from `start_at` to `end_at`. It is an ordinary resident-scoped resource (a tuple in `_RESIDENT_RESOURCES`, `assignments` permission group) with a bespoke `CareVisitService` that applies `ensure_can_care` and refuses overlapping visits for the same carer (409). `GET /care-schedule?start=&end=` returns a time window for the dashboard's daily roster, which draws each visit inside the carer's shift bar. Double-booking is checked only in the app, not by a DB exclusion constraint. `POST /residents/{id}/care-visits/next-free-hour` books the carer's first free whole hour on shift for the rest of the day, or returns `null`. `SuggestedCarers` calls it straight after an assignment so the new match appears on today's dashboard.

4. **Standalone bespoke resources** (`complaints` → `complaints_feedback` table, `appointments`) have no required parent — optional `resident_id`/`employee_id` links (complaints) or none at all (appointments, a public-submittable enquiry with no resident/employee link by design). Each mirrors `residents`/`employees`: own model/schema/repository/endpoint files, `CrudService`, single flat router (no nesting), full CRUD. `AppointmentCreate` only accepts the publicly-submittable fields (name/email/phone/type/preferred date-time/message) — `status`/`scheduled_at`/`handled_by`/`admin_notes` are admin-only, settable only via `AppointmentUpdate`.

5. **Computed resources** (`risk-scores`, `shift-suggestions`, `roster/optimise`, `risk-weights`, `suggested-carers`, `coverage/suggest-assignments`) have no table of their own — they compute a response from other tables on the fly and write nothing:
   - `backend/services/risk_scoring.py` (`RiskScoringService`) — an additive weighted model over a resident's fall-risk level, recent incidents, assistance level, cognitive status and behaviour frequency. Each signal is normalised to [0,1], multiplied by its **AHP-derived** weight (see Algorithms below) and scaled to 100, so the per-signal breakdown sums exactly to the score. `GET /risk-scores` and `GET /residents/{id}/risk-score`.
   - `backend/services/shift_matching.py` (`ShiftMatchingService`) + `backend/services/employee_care_load.py` — ranks candidates for **one** shift, for a human to pick from. `GET /shifts/{id}/suggested-employees`.
     **Note:** `employee_care_load.py` still infers care load from the `assessed_by`/`reported_by`/`recorded_by`/`updated_by` author columns, which was the only option before `resident_assignments` existed. Now that real assignments are recorded, `AssignmentService.get_caseload` computes the same quantity properly (`total_risk_load`). Switching the care-load helper onto real assignments is a one-function change that has deliberately not been made yet.
   - `backend/services/roster_optimisation.py` (`RosterOptimisationService`) — recommends staff for **many** shifts in time order (SAW + lexicographic ranking). `POST /roster/optimise`.
   - `backend/services/carer_matching.py` (`CarerMatchingService`) — the same pair of answers for care assignments rather than shifts: `GET /residents/{id}/suggested-carers` ranks candidates for one resident (staff on shift that day first, then SAW, then caseload; the browser passes its local `day_start`/`day_end`), `POST /coverage/suggest-assignments` allocates a primary carer to every resident missing one, in one ranked pass. Both are guarded by the `assignments` group, so the POST is a clinical-staff action while the GET is readable by anyone who can see a care team. **Neither writes** — `POST /coverage/assignments` (`AssignmentService.create_many`) is the separate step that turns a reviewed plan into rows.
   - These parallelize their independent Supabase lookups with `asyncio.gather` rather than awaiting sequentially — this matters because each computation is several round-trips deep (score a resident → 4 queries; the optimiser fetches each candidate's profile once, then every matrix cell is pure arithmetic).

### Algorithms (`backend/algorithms/`)

Self-contained, dependency-free, with no knowledge of FastAPI or Supabase. Full explanation in `docs/ALGORITHMS.md`; viva answers in `docs/VIVA_ALGORITHMS.md`; runnable demo: `uv run python -m backend.scripts.demo_decision_algorithms`.

1. **`saw.py` — Simple Additive Weighting.** `S = Σ(w × r)` with min-max normalised criteria (`normalize_benefit` / `normalize_cost`, equal min/max → 1.0). Higher score is always better, 0–1. `saw_breakdown` gives the per-criterion explanation returned by the API.
2. **`lexicographic.py` — `rank(items, priority)`.** Tuple sort on `((field, higher_is_better), ...)`. Hard rules (conflict, role, active) are priorities here, never SAW weights.
3. **`ahp.py` — Analytic Hierarchy Process.** Derives the resident risk weights from `JUDGEMENTS` in `backend/config/risk_weights.py`; `test_ahp.py` fails if the judgements become inconsistent (CR ≥ 0.10).

Where used: `risk_scoring.py` (SAW), `carer_matching.py` and `shift_matching.py` (SAW + lexicographic; weights and priority are the `*_WEIGHTS` / `*_PRIORITY` constants at the top of each file), `roster_optimisation.py` (`POST /roster/optimise`, shifts in time order reusing `rank_shift_candidates`, remembering each recommendation so nobody is double-booked; a recommendation, not a global optimum). `POST /coverage/suggest-assignments` works the same way, highest-risk resident first, adding each pick to that carer's load. The Hungarian algorithm was removed.

**Note:** `employee_care_load.py` still infers care load from the `assessed_by`/`reported_by`/`recorded_by`/`updated_by` author columns; `AssignmentService.get_caseload` computes the real quantity from `resident_assignments`. Switching is a one-function change that has deliberately not been made.

### Supabase access

- A single `AsyncClient` is created on startup (`backend/main.py` lifespan → `backend/db/supabase_client.py`) and fetched per-request via `get_supabase()`. There is no connection pooling logic to manage — Supabase's client handles it.
- Repositories talk to Supabase's `.table(...).select/insert/update/delete()` query builder directly; there is no ORM layer.
- **The schema lives in `backend/sql/000_schema.sql`** — all 27 tables, generated from the Pydantic models by `backend/scripts/generate_schema.py`, plus hand-written hardening (audit append-only triggers, RLS on `users`/`audit_log`, the lowercase-email constraint). It is idempotent: every statement uses `IF NOT EXISTS`, so it is safe to run against a database that already has some tables. Verified by applying it twice to a clean Postgres 16, and once on top of a database already holding the original `residents`/`employees` tables with data.
- After changing a model, regenerate rather than hand-editing the SQL:
  ```bash
  uv run python -m backend.scripts.generate_schema > backend/sql/000_schema.sql
  ```
  Then re-append the hardening block at the end of that file (the generator does not emit it — those rules have no equivalent in a Pydantic model).
- Models generally carry `created_at`/`updated_at` and are dumped with `mode="json"` before insert/update so `date`/`datetime`/`UUID`/enum values serialize correctly for Supabase.

### Auth and authorisation

Enforced, not scaffolding. Three pieces:

1. **Authentication** — `backend/config/security.py` (bcrypt hashing, JWT encode/decode), `backend/models/user.py`, `backend/repositories/user_repository.py`, `backend/services/auth_service.py`, `backend/api/v1/endpoints/auth.py`. Logins are throttled after 5 failures in 15 minutes (`services/login_throttle.py`, in-process — see the note in that file before scaling to multiple workers). Passwords are SHA-256 pre-hashed before bcrypt so bcrypt's 72-byte limit cannot truncate a long passphrase or raise.

2. **Authorisation** — `backend/config/permissions.py` holds the whole matrix: resource group → {read: roles, write: roles}. `require_permission(group)` in `backend/api/auth_deps.py` reads the request method and checks it. Guards are applied **once per router** in `router.py`, never per route, so a new resource is protected by adding one string to its tuple. `AccessRole` (Admin/Manager/Nurse/Care Worker/Family) is separate from `EmployeeRole` (job title) on purpose.

   **To add a new protected resource**: add its permission group to the matrix if it needs a new one, then pass that group name as the 6th element of the tuple in `_RESIDENT_RESOURCES`/`_EMPLOYEE_RESOURCES`. `backend/tests/test_permissions.py::test_no_route_is_left_unguarded` fails if you forget.

3. **Audit** — every create/update/delete is recorded by the repository layer (`repositories/audited.py`, mixed into `SupabaseRepository` and each bespoke repository) with a from→to diff of only the changed fields; logins, failed logins, password changes and refused requests are recorded by the auth layer. The actor travels via a `ContextVar` (`backend/core/request_context.py`) set by `get_current_user`, so no service signature had to grow an actor argument. `audit_log` is append-only, enforced by Postgres triggers as well as by having no write route. Audit failures are logged and swallowed — they must never turn a successful clinical write into a 500.

Note the `roster_planning` group, added for `POST /roster/optimise`. The endpoint stores nothing, but it is a POST (the body carries a list of shifts), and `analytics` is deliberately write-empty. Rather than give `analytics` a write audience just to let one endpoint through — which would have weakened a group whose whole point is being read-only — running the optimiser got its own group, restricted to leadership. `roster.py` therefore exports two routers, mounted with different guards.

The only unauthenticated endpoints are `/health`, `/auth/login` and `POST /appointments/public`. That last one is the public landing-page form: its own module (`endpoints/public_appointments.py`), its own schema with a honeypot field, IP rate limiting, and an acknowledgement-only response that reveals no stored record. The admin `/appointments` routes require a signed-in staff account.

## Frontend (`frontend/`)

Vite + React 18, plain JavaScript/JSX (no TypeScript), `react-router-dom`, plain CSS with custom properties (no Tailwind/UI kit), native `fetch()` (no axios) — deliberately minimal dependencies throughout.

### Routing split

`frontend/src/App.jsx`: `/` is the public landing page (`pages/PublicLandingPage.jsx`, no sidebar) — a one-shot appointment-request form posting to `/appointments/public`, not built on the admin resource machinery. Everything else lives under `/admin/*`, wrapped in `RequireAuth`, individual `RequireRole` guards, `AppShell` (sidebar nav) and `DirectoryProvider` (loads the full residents/employees lists once for name lookups and `ReferenceSelect` dropdowns) — **both are scoped to the `/admin` route tree only**, not mounted globally, so the public page never fetches admin data.

### The core pattern: one generic `ResourcePanel`, driven by config

Mirrors the backend's own generic parent-scoped-resource philosophy. Instead of a hand-written page per resource, every admin CRUD screen is `<ResourcePanel resource={someConfig} parentId={optional} />`:
- `components/resource/ResourcePanel.jsx` / `ResourceTable.jsx` / `ResourceForm.jsx` — generic list + create/edit modal + delete, driven entirely by a config object.
- `config/*.config.js` — one config per resource (`residents.config.js`, `employees.config.js`, `complaints.config.js`, `appointments.config.js`, `residentResourceConfigs.js`, `employeeResourceConfigs.js`). Each field declares `type` (`text`/`textarea`/`number`/`date`/`time`/`datetime`/`boolean`/`enum`/`reference`/`group`), `required`, `editOnly` (admin-only fields hidden on create — e.g. appointment `status`/`admin_notes`), and for `reference` fields, what they point at.
- `config/enums.js` — every backend `StrEnum`'s literal values, must byte-match exactly (a mismatch is a silent 422, not a frontend error).
- **To add a new admin-manageable resource**: add a config object + a one-line `<ResourcePanel resource={...} />` page. No new table/form component needed.

Three reference shapes exist (`components/common/ReferenceSelect.jsx`): global lookup (`residents`/`employees`, backed by `DirectoryContext`), parent-scoped (`time_entries.shift_id`, looks up the current employee's own shifts), and plain free text that merely looks like a reference (`medications.prescribed_by`) — reference-ness is always an explicit config flag, never inferred from the field name.

The public landing page reuses `appointmentsConfig` (filtering out `editOnly` fields) for its form fields, so the public and admin forms can't drift out of sync, but does **not** use `ResourcePanel` — a visitor needs a one-shot form with a success state, not a data table.

### Auth on the frontend

`context/AuthContext.jsx` holds the session; `api/client.js` attaches the bearer token, applies a 15s timeout, supports `AbortSignal`, and broadcasts an `unauthorized` event on any 401 that the context listens for and signs out on. `config/permissions.js` is a hand-maintained mirror of the backend matrix used only to decide what to render — hiding a nav link a role cannot use. **It is not a security boundary**; keep it in step with `backend/config/permissions.py` when that changes.

**There is no Algorithms page, and adding one back would be a mistake.** There was: a standalone `/admin/algorithms` screen demonstrating an allocation demo and the AHP weights side by side. It was deleted because nobody navigates to a screen to admire an algorithm — the output has to arrive where the decision is made, or it is a demo rather than a feature. The same work now surfaces in two places:

- `components/residents/SuggestedCarers.jsx` — a ranked candidate list rendered immediately above "Manage assignments" on a resident's Care Team tab, from `GET /residents/{id}/suggested-carers`. Every candidate carries the reason it was ranked there, because a suggestion nobody can interrogate gets rubber-stamped or ignored, and each can be assigned in one click. The offered type follows `has_primary` from the care team: Primary when the resident has no key worker, Secondary once they do.
- `components/coverage/AllocationPlan.jsx` — the whole-facility allocation on `/admin/coverage`, from `POST /coverage/suggest-assignments`, sitting directly under the list of residents missing a key worker. Run on demand, never on page load. Every row can be re-pointed at a different carer (the plan ships `alternatives` per resident so editing costs no request) or unticked entirely, and **Confirm** posts only what survived that review. Its footnote reports how many residents were ranked and how many could not be matched.

Risk scores are still computed by the API (`/risk-scores`, `/risk-weights`) and feed the suggestions, but the frontend deliberately does not display them. Both suggestion surfaces return `null` unless `can("assignments", "write")`: a care worker reads the care team but does not decide it, and advice you cannot act on is noise. The `algo-*` CSS classes in `layout.css` are the leftover vocabulary from the deleted page, reused by these three.

**Propose, amend, confirm — three steps, deliberately.** The cost function knows about workload and clinical scope and knows nothing about who a resident actually gets on with, so a plan that applied itself would be asking to be trusted about something it cannot see. Nothing is written until a person confirms, and what is written is what they approved, not what was proposed.

The bulk write is **not all-or-nothing**. Between proposing and confirming, someone else may name a primary carer for one of those residents; rejecting the batch over that would discard nine good assignments to punish one stale row. `create_many` applies each line through the ordinary `create_assignment` — same rules, same audit trail — and returns `{created, failed}` with the real rejection message per line, always 200. `create_many` is sequential rather than gathered because two lines can name the same resident, and concurrent reads would both see "no primary yet".

`ApplyResult` is rendered by `CoveragePage`, not by `AllocationPlan`: confirming can fill the last gap, which removes the panel, and the report of what happened must not vanish with it. A batch containing any failure is toned as a warning rather than a success, and drops the "every resident now has a key worker" line, which would otherwise be false above a list of the ones who do not.

**Staff (HR) vs Login Accounts.** Two nav entries that sound similar and are not: `employees` is the employment record (job title, contract, qualifications, shifts), `users` is a way to sign in (email, password hash, access role). Not every employee needs an account, a family login will have no employment record, and a Care Coordinator may hold Manager access. `users.employee_id` links them where both exist. Both pages carry copy explaining the split.

The **Coverage** page (`/admin/coverage`) reads `GET /coverage`; resident detail gains a **Care Team** tab and employee detail an **Assigned Residents** tab, both backed by the enriched assignment views.

`RequireRole` guards a whole page, `IfAllowed` hides a single control. `ErrorBoundary` (keyed on the route path) stops one broken screen blanking the console. `ResourceForm` supports three field visibility flags: `editOnly` (hidden on create), `createOnly` (hidden on edit — a password), and `readOnly` (never in a form, still in the table).

### Design system

`styles/tokens.css` — two-tone brand (teal primary + coral secondary, both with gradient variants) for the UI shell, plus a separate 5-tone semantic set (neutral/info/success/warning/danger) used only for status badges via `config/badgeTones.js` (maps each enum literal to a tone — forcing every status into two brand hues would make badges unreadable). `components/layout/Icons.jsx` is a small hand-drawn inline SVG icon set (no icon library).
