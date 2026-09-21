-- ===========================================================================
-- CareOS — complete database schema
--
-- Generated from the Pydantic models in backend/models/.
-- Regenerate rather than hand-edit: the models are the source of truth.

-- ----------------------------------------------------------------------
-- residents
-- ----------------------------------------------------------------------
create table if not exists public.residents (
    id                     uuid not null default gen_random_uuid(),
    first_name             text not null,
    last_name              text not null,
    dob                    date null,
    gender                 text null,
    cognitive_status       text null,
    room_number            text null,
    admission_date         date null,
    emergency_contact      jsonb null,
    active                 boolean null default true,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint residents_pkey primary key (id),
    constraint residents_cognitive_status_check
        check (cognitive_status is null or cognitive_status = any (array['Cognitive', 'Non-Cognitive', 'Disabled-Cognitive', 'Disabled-Non-Cognitive']::text[]))
);

-- ----------------------------------------------------------------------
-- employees
-- ----------------------------------------------------------------------
create table if not exists public.employees (
    id                     uuid not null default gen_random_uuid(),
    first_name             text not null,
    last_name              text not null,
    email                  text null,
    phone                  text null,
    role                   text null,
    employment_status      text null,
    hire_date              date null,
    termination_date       date null,
    active                 boolean null default true,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint employees_pkey primary key (id),
    constraint employees_role_check
        check (role is null or role = any (array['Care Planner', 'Care Coordinator', 'Registered Nurse', 'Kitchen Staff', 'Laundry Staff', 'Administrator', 'Manager']::text[])),
    constraint employees_employment_status_check
        check (employment_status is null or employment_status = any (array['Full-Time', 'Part-Time', 'Casual', 'Agency']::text[]))
);

-- ----------------------------------------------------------------------
-- users
-- ----------------------------------------------------------------------
create table if not exists public.users (
    id                     uuid not null default gen_random_uuid(),
    email                  text not null,
    password_hash          text not null,
    access_role            text not null,
    employee_id            uuid null,
    full_name              text null,
    active                 boolean null default true,
    last_login_at          timestamptz null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint users_pkey primary key (id),
    constraint users_access_role_check
        check (access_role is null or access_role = any (array['Admin', 'Manager', 'Nurse', 'Care Worker', 'Family']::text[])),
    constraint users_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete set null
);
create index if not exists users_employee_id_idx on public.users (employee_id);

-- ----------------------------------------------------------------------
-- audit_log
-- ----------------------------------------------------------------------
create table if not exists public.audit_log (
    id                     uuid not null default gen_random_uuid(),
    action                 text not null,
    table_name             text not null,
    record_id              text null,
    actor_id               uuid null,
    actor_email            text null,
    actor_role             text null,
    request_id             text null,
    ip_address             text null,
    changes                jsonb null,
    detail                 text null,
    created_at             timestamptz not null default now(),
    constraint audit_log_pkey primary key (id),
    constraint audit_log_action_check
        check (action is null or action = any (array['create', 'update', 'delete', 'login', 'login_failed', 'password_change', 'access_denied']::text[]))
);

-- ----------------------------------------------------------------------
-- appointments
-- ----------------------------------------------------------------------
create table if not exists public.appointments (
    id                     uuid not null default gen_random_uuid(),
    full_name              text not null,
    email                  text not null,
    phone                  text null,
    appointment_type       text not null,
    preferred_date         date null,
    preferred_time         time null,
    message                text null,
    status                 text null default 'Pending',
    scheduled_at           timestamptz null,
    handled_by             uuid null,
    admin_notes            text null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint appointments_pkey primary key (id),
    constraint appointments_status_check
        check (status is null or status = any (array['Pending', 'Confirmed', 'Cancelled', 'Completed']::text[])),
    constraint appointments_handled_by_fkey
        foreign key (handled_by) references public.employees (id) on delete set null
);
create index if not exists appointments_handled_by_idx on public.appointments (handled_by);

-- ----------------------------------------------------------------------
-- complaints_feedback
-- ----------------------------------------------------------------------
create table if not exists public.complaints_feedback (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    employee_id            uuid null,
    category               text not null,
    description            text not null,
    submitted_by_name      text not null,
    submitted_by_relationship text null,
    submitted_by_contact   text null,
    is_anonymous           boolean null default false,
    status                 text null default 'Open',
    assigned_to            uuid null,
    resolution_notes       text null,
    resolved_at            timestamptz null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint complaints_feedback_pkey primary key (id),
    constraint complaints_feedback_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete set null,
    constraint complaints_feedback_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete set null,
    constraint complaints_feedback_status_check
        check (status is null or status = any (array['Open', 'Investigating', 'Resolved', 'Closed']::text[]))
);
create index if not exists complaints_feedback_resident_id_idx on public.complaints_feedback (resident_id);
create index if not exists complaints_feedback_employee_id_idx on public.complaints_feedback (employee_id);

-- ----------------------------------------------------------------------
-- resident_medical_history
-- ----------------------------------------------------------------------
create table if not exists public.resident_medical_history (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    diagnosis              text null,
    allergies              text null,
    chronic_conditions     text null,
    surgeries              text null,
    doctor_name            text null,
    notes                  text null,
    recorded_at            timestamptz null,
    constraint resident_medical_history_pkey primary key (id),
    constraint resident_medical_history_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade
);
create index if not exists resident_medical_history_resident_id_idx on public.resident_medical_history (resident_id);

-- ----------------------------------------------------------------------
-- resident_assignments
-- ----------------------------------------------------------------------
create table if not exists public.resident_assignments (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    employee_id            uuid null,
    assignment_type        text null default 'Secondary',
    start_date             date null,
    end_date               date null,
    active                 boolean null default true,
    notes                  text null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint resident_assignments_pkey primary key (id),
    constraint resident_assignments_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade,
    constraint resident_assignments_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade,
    constraint resident_assignments_assignment_type_check
        check (assignment_type is null or assignment_type = any (array['Primary', 'Secondary', 'Relief']::text[]))
);
create index if not exists resident_assignments_resident_id_idx on public.resident_assignments (resident_id);
create index if not exists resident_assignments_employee_id_idx on public.resident_assignments (employee_id);

-- ----------------------------------------------------------------------
-- resident_behaviour
-- ----------------------------------------------------------------------
create table if not exists public.resident_behaviour (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    behaviour              text null,
    trigger                text null,
    intervention           text null,
    outcome                text null,
    recorded_by            uuid null,
    recorded_at            timestamptz null,
    constraint resident_behaviour_pkey primary key (id),
    constraint resident_behaviour_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade,
    constraint resident_behaviour_recorded_by_fkey
        foreign key (recorded_by) references public.employees (id) on delete set null
);
create index if not exists resident_behaviour_resident_id_idx on public.resident_behaviour (resident_id);
create index if not exists resident_behaviour_recorded_by_idx on public.resident_behaviour (recorded_by);

-- ----------------------------------------------------------------------
-- resident_medications
-- ----------------------------------------------------------------------
create table if not exists public.resident_medications (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    medication_name        text null,
    dosage                 text null,
    frequency              text null,
    route                  text null,
    prescribed_by          text null,
    start_date             date null,
    end_date               date null,
    active                 boolean null default true,
    notes                  text null,
    constraint resident_medications_pkey primary key (id),
    constraint resident_medications_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade
);
create index if not exists resident_medications_resident_id_idx on public.resident_medications (resident_id);

-- ----------------------------------------------------------------------
-- resident_bowel_chart
-- ----------------------------------------------------------------------
create table if not exists public.resident_bowel_chart (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    recorded_at            timestamptz null,
    bowel_type             text null,
    consistency            text null,
    notes                  text null,
    recorded_by            uuid null,
    constraint resident_bowel_chart_pkey primary key (id),
    constraint resident_bowel_chart_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade,
    constraint resident_bowel_chart_recorded_by_fkey
        foreign key (recorded_by) references public.employees (id) on delete set null
);
create index if not exists resident_bowel_chart_resident_id_idx on public.resident_bowel_chart (resident_id);
create index if not exists resident_bowel_chart_recorded_by_idx on public.resident_bowel_chart (recorded_by);

-- ----------------------------------------------------------------------
-- resident_sleep_chart
-- ----------------------------------------------------------------------
create table if not exists public.resident_sleep_chart (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    sleep_date             date null,
    sleep_start            time null,
    wake_time              time null,
    total_hours            numeric(12, 2) null,
    disturbances           text null,
    recorded_by            uuid null,
    constraint resident_sleep_chart_pkey primary key (id),
    constraint resident_sleep_chart_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade,
    constraint resident_sleep_chart_recorded_by_fkey
        foreign key (recorded_by) references public.employees (id) on delete set null
);
create index if not exists resident_sleep_chart_resident_id_idx on public.resident_sleep_chart (resident_id);
create index if not exists resident_sleep_chart_recorded_by_idx on public.resident_sleep_chart (recorded_by);

-- ----------------------------------------------------------------------
-- resident_fall_risk
-- ----------------------------------------------------------------------
create table if not exists public.resident_fall_risk (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    risk_level             text null,
    assessment_date        date null,
    assessed_by            uuid null,
    interventions          text null,
    notes                  text null,
    constraint resident_fall_risk_pkey primary key (id),
    constraint resident_fall_risk_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade,
    constraint resident_fall_risk_risk_level_check
        check (risk_level is null or risk_level = any (array['Low', 'Medium', 'High']::text[])),
    constraint resident_fall_risk_assessed_by_fkey
        foreign key (assessed_by) references public.employees (id) on delete set null
);
create index if not exists resident_fall_risk_resident_id_idx on public.resident_fall_risk (resident_id);
create index if not exists resident_fall_risk_assessed_by_idx on public.resident_fall_risk (assessed_by);

-- ----------------------------------------------------------------------
-- resident_assistance
-- ----------------------------------------------------------------------
create table if not exists public.resident_assistance (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    assistance_level       text null,
    mobility               text null,
    transfer_notes         text null,
    updated_by             uuid null,
    updated_at             timestamptz not null default now(),
    constraint resident_assistance_pkey primary key (id),
    constraint resident_assistance_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade,
    constraint resident_assistance_assistance_level_check
        check (assistance_level is null or assistance_level = any (array['Independent', 'Single Assist', 'Double Assist']::text[])),
    constraint resident_assistance_updated_by_fkey
        foreign key (updated_by) references public.employees (id) on delete set null
);
create index if not exists resident_assistance_resident_id_idx on public.resident_assistance (resident_id);
create index if not exists resident_assistance_updated_by_idx on public.resident_assistance (updated_by);

-- ----------------------------------------------------------------------
-- resident_medical_inventory
-- ----------------------------------------------------------------------
create table if not exists public.resident_medical_inventory (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    item_name              text null,
    quantity               integer null,
    unit                   text null,
    expiry_date            date null,
    notes                  text null,
    added_by               uuid null,
    created_at             timestamptz not null default now(),
    constraint resident_medical_inventory_pkey primary key (id),
    constraint resident_medical_inventory_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade
);
create index if not exists resident_medical_inventory_resident_id_idx on public.resident_medical_inventory (resident_id);

-- ----------------------------------------------------------------------
-- resident_incidents
-- ----------------------------------------------------------------------
create table if not exists public.resident_incidents (
    id                     uuid not null default gen_random_uuid(),
    resident_id            uuid null,
    incident_type          text not null,
    severity               text not null,
    description            text not null,
    occurred_at            timestamptz not null,
    location               text null,
    reported_by            uuid null,
    witnesses              text null,
    immediate_action       text null,
    is_sirs_reportable     boolean null default false,
    sirs_notified_at       timestamptz null,
    sirs_reference_number  text null,
    status                 text null default 'Open',
    outcome                text null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint resident_incidents_pkey primary key (id),
    constraint resident_incidents_resident_id_fkey
        foreign key (resident_id) references public.residents (id) on delete cascade,
    constraint resident_incidents_severity_check
        check (severity is null or severity = any (array['Low', 'Medium', 'High', 'Critical']::text[])),
    constraint resident_incidents_reported_by_fkey
        foreign key (reported_by) references public.employees (id) on delete set null,
    constraint resident_incidents_status_check
        check (status is null or status = any (array['Open', 'Under Review', 'Reported', 'Closed']::text[]))
);
create index if not exists resident_incidents_resident_id_idx on public.resident_incidents (resident_id);
create index if not exists resident_incidents_reported_by_idx on public.resident_incidents (reported_by);

-- ----------------------------------------------------------------------
-- employee_supervision
-- ----------------------------------------------------------------------
create table if not exists public.employee_supervision (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    supervisor             uuid null,
    supervision_date       date null,
    discussion             text null,
    action_items           text null,
    follow_up_date         date null,
    constraint employee_supervision_pkey primary key (id),
    constraint employee_supervision_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade
);
create index if not exists employee_supervision_employee_id_idx on public.employee_supervision (employee_id);

-- ----------------------------------------------------------------------
-- employee_registration
-- ----------------------------------------------------------------------
create table if not exists public.employee_registration (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    registration_type      text null,
    registration_number    text null,
    issuing_authority      text null,
    issue_date             date null,
    expiry_date            date null,
    verified               boolean null default false,
    constraint employee_registration_pkey primary key (id),
    constraint employee_registration_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade
);
create index if not exists employee_registration_employee_id_idx on public.employee_registration (employee_id);

-- ----------------------------------------------------------------------
-- employee_qualifications
-- ----------------------------------------------------------------------
create table if not exists public.employee_qualifications (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    qualification_name     text null,
    institution            text null,
    completion_date        date null,
    expiry_date            date null,
    constraint employee_qualifications_pkey primary key (id),
    constraint employee_qualifications_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade
);
create index if not exists employee_qualifications_employee_id_idx on public.employee_qualifications (employee_id);

-- ----------------------------------------------------------------------
-- employee_performance
-- ----------------------------------------------------------------------
create table if not exists public.employee_performance (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    reviewer               uuid null,
    review_date            date null,
    overall_rating         integer null,
    strengths              text null,
    improvements           text null,
    goals                  text null,
    next_review            date null,
    constraint employee_performance_pkey primary key (id),
    constraint employee_performance_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade
);
create index if not exists employee_performance_employee_id_idx on public.employee_performance (employee_id);

-- ----------------------------------------------------------------------
-- employee_leave
-- ----------------------------------------------------------------------
create table if not exists public.employee_leave (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    leave_type             text null,
    start_date             date null,
    end_date               date null,
    status                 text null,
    approved_by            uuid null,
    notes                  text null,
    constraint employee_leave_pkey primary key (id),
    constraint employee_leave_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade,
    constraint employee_leave_status_check
        check (status is null or status = any (array['Pending', 'Approved', 'Rejected', 'Cancelled']::text[])),
    constraint employee_leave_approved_by_fkey
        foreign key (approved_by) references public.employees (id) on delete set null
);
create index if not exists employee_leave_employee_id_idx on public.employee_leave (employee_id);
create index if not exists employee_leave_approved_by_idx on public.employee_leave (approved_by);

-- ----------------------------------------------------------------------
-- employee_contracts
-- ----------------------------------------------------------------------
create table if not exists public.employee_contracts (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    contract_type          text null,
    contracted_hours       numeric(12, 2) null,
    hourly_rate            numeric(12, 2) null,
    start_date             date null,
    end_date               date null,
    annual_leave_hours     numeric(12, 2) null,
    sick_leave_hours       numeric(12, 2) null,
    notes                  text null,
    constraint employee_contracts_pkey primary key (id),
    constraint employee_contracts_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade
);
create index if not exists employee_contracts_employee_id_idx on public.employee_contracts (employee_id);

-- ----------------------------------------------------------------------
-- employee_availability
-- ----------------------------------------------------------------------
create table if not exists public.employee_availability (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    weekday                text null,
    start_time             time null,
    end_time               time null,
    available              boolean null default true,
    constraint employee_availability_pkey primary key (id),
    constraint employee_availability_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade
);
create index if not exists employee_availability_employee_id_idx on public.employee_availability (employee_id);

-- ----------------------------------------------------------------------
-- employee_shifts
-- ----------------------------------------------------------------------
create table if not exists public.employee_shifts (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    shift_start            timestamptz not null,
    shift_end              timestamptz not null,
    role                   text null,
    location               text null,
    status                 text null default 'Scheduled',
    notes                  text null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint employee_shifts_pkey primary key (id),
    constraint employee_shifts_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade,
    constraint employee_shifts_status_check
        check (status is null or status = any (array['Scheduled', 'Confirmed', 'Completed', 'Cancelled', 'No-Show']::text[]))
);
create index if not exists employee_shifts_employee_id_idx on public.employee_shifts (employee_id);

-- ----------------------------------------------------------------------
-- employee_time_entries
-- ----------------------------------------------------------------------
create table if not exists public.employee_time_entries (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    shift_id               uuid null,
    clock_in               timestamptz not null,
    clock_out              timestamptz null,
    notes                  text null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint employee_time_entries_pkey primary key (id),
    constraint employee_time_entries_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade,
    constraint employee_time_entries_shift_id_fkey
        foreign key (shift_id) references public.employee_shifts (id) on delete set null
);
create index if not exists employee_time_entries_employee_id_idx on public.employee_time_entries (employee_id);
create index if not exists employee_time_entries_shift_id_idx on public.employee_time_entries (shift_id);

-- ----------------------------------------------------------------------
-- employee_payroll_records
-- ----------------------------------------------------------------------
create table if not exists public.employee_payroll_records (
    id                     uuid not null default gen_random_uuid(),
    employee_id            uuid null,
    pay_period_start       date not null,
    pay_period_end         date not null,
    total_hours            numeric(12, 2) null,
    hourly_rate            numeric(12, 2) null,
    gross_pay              numeric(12, 2) null,
    deductions             numeric(12, 2) null,
    net_pay                numeric(12, 2) null,
    status                 text null default 'Draft',
    notes                  text null,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    constraint employee_payroll_records_pkey primary key (id),
    constraint employee_payroll_records_employee_id_fkey
        foreign key (employee_id) references public.employees (id) on delete cascade,
    constraint employee_payroll_records_status_check
        check (status is null or status = any (array['Draft', 'Finalized', 'Paid']::text[]))
);
create index if not exists employee_payroll_records_employee_id_idx on public.employee_payroll_records (employee_id);


-- A resident has at most one primary carer at a time. Enforced here as well
-- as in AssignmentService, because "exactly one key worker" is a rule about
-- the data, not about one code path that happens to check it.
create unique index if not exists resident_assignments_one_primary_idx
    on public.resident_assignments (resident_id)
    where (assignment_type = 'Primary' and active = true);

-- The same employee must not be assigned twice to the same resident.
create unique index if not exists resident_assignments_unique_active_idx
    on public.resident_assignments (resident_id, employee_id)
    where (active = true);

-- ===========================================================================
-- Auth and audit hardening
-- ===========================================================================

-- Email is the login identifier, so it must be unique. Lower-cased by the
-- application before every write; enforced here too so a direct SQL insert
-- cannot create a duplicate differing only by case.
create unique index if not exists users_email_key on public.users (lower(email));

alter table public.users drop constraint if exists users_email_lowercase_check;
alter table public.users add constraint users_email_lowercase_check
    check (email = lower(email));

create index if not exists users_access_role_idx on public.users (access_role);

-- The two queries the audit UI actually runs: newest-first overall, and the
-- full history of one specific record.
create index if not exists audit_log_created_at_idx on public.audit_log (created_at desc);
create index if not exists audit_log_record_idx on public.audit_log (table_name, record_id);
create index if not exists audit_log_actor_idx on public.audit_log (actor_id);

-- Append-only, enforced by the database rather than by convention. Without
-- this, "immutable history" is only true for as long as every future code
-- path remembers to be careful.
create or replace function public.audit_log_is_append_only()
returns trigger
language plpgsql
as $$
begin
    raise exception 'audit_log is append-only; % is not permitted', tg_op;
end;
$$;

drop trigger if exists audit_log_no_update on public.audit_log;
create trigger audit_log_no_update
    before update on public.audit_log
    for each row execute function public.audit_log_is_append_only();

drop trigger if exists audit_log_no_delete on public.audit_log;
create trigger audit_log_no_delete
    before delete on public.audit_log
    for each row execute function public.audit_log_is_append_only();

-- ===========================================================================
-- Row Level Security on the two sensitive tables
-- ===========================================================================
-- The API connects with the service key and enforces authorisation itself
-- (backend/config/permissions.py), so RLS is a second fence: it stops an
-- anon/public key that leaks into the frontend bundle from reading password
-- hashes or the audit trail. No permissive policies are created, so anon and
-- authenticated keys get nothing. The service key bypasses RLS by design, so
-- the API is unaffected.
alter table public.users enable row level security;
alter table public.audit_log enable row level security;
