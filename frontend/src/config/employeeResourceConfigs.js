import { LEAVE_STATUS, SHIFT_STATUS, PAYROLL_STATUS } from "./enums.js";

const employeeRef = {
  type: "reference",
  reference: { resource: "employees", scope: "global", labelFields: ["first_name", "last_name"] },
};

export const supervision = {
  slug: "supervision",
  label: "Supervision Record",
  parent: { resource: "employees" },
  timestampField: null,
  fields: [
    { name: "supervisor", label: "Supervisor", ...employeeRef },
    { name: "supervision_date", label: "Supervision Date", type: "date" },
    { name: "discussion", label: "Discussion", type: "textarea" },
    { name: "action_items", label: "Action Items", type: "textarea" },
    { name: "follow_up_date", label: "Follow-up Date", type: "date" },
  ],
};

export const registration = {
  slug: "registration",
  label: "Registration",
  parent: { resource: "employees" },
  timestampField: null,
  fields: [
    { name: "registration_type", label: "Type", type: "text" },
    { name: "registration_number", label: "Registration #", type: "text" },
    { name: "issuing_authority", label: "Issuing Authority", type: "text" },
    { name: "issue_date", label: "Issue Date", type: "date" },
    { name: "expiry_date", label: "Expiry Date", type: "date" },
    { name: "verified", label: "Verified", type: "boolean", badgeKind: "verified", defaultValue: false },
  ],
};

export const qualifications = {
  slug: "qualifications",
  label: "Qualification",
  parent: { resource: "employees" },
  timestampField: null,
  fields: [
    { name: "qualification_name", label: "Qualification", type: "text" },
    { name: "institution", label: "Institution", type: "text" },
    { name: "completion_date", label: "Completion Date", type: "date" },
    { name: "expiry_date", label: "Expiry Date", type: "date" },
  ],
};

export const performance = {
  slug: "performance",
  label: "Performance Review",
  parent: { resource: "employees" },
  timestampField: null,
  fields: [
    { name: "reviewer", label: "Reviewer", ...employeeRef },
    { name: "review_date", label: "Review Date", type: "date" },
    { name: "overall_rating", label: "Overall Rating (1-5)", type: "number" },
    { name: "strengths", label: "Strengths", type: "textarea" },
    { name: "improvements", label: "Improvements", type: "textarea" },
    { name: "goals", label: "Goals", type: "textarea" },
    { name: "next_review", label: "Next Review", type: "date" },
  ],
};

export const leave = {
  slug: "leave",
  label: "Leave Request",
  parent: { resource: "employees" },
  timestampField: null,
  fields: [
    { name: "leave_type", label: "Leave Type", type: "text" },
    { name: "start_date", label: "Start Date", type: "date" },
    { name: "end_date", label: "End Date", type: "date" },
    {
      name: "status",
      label: "Status",
      type: "enum",
      options: LEAVE_STATUS,
      defaultValue: "Pending",
      badgeKind: "leaveStatus",
    },
    { name: "approved_by", label: "Approved By", ...employeeRef },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const contracts = {
  slug: "contracts",
  label: "Contract",
  parent: { resource: "employees" },
  timestampField: null,
  fields: [
    { name: "contract_type", label: "Contract Type", type: "text" },
    { name: "contracted_hours", label: "Contracted Hours", type: "number" },
    { name: "hourly_rate", label: "Hourly Rate", type: "number" },
    { name: "start_date", label: "Start Date", type: "date" },
    { name: "end_date", label: "End Date", type: "date" },
    { name: "annual_leave_hours", label: "Annual Leave Hours", type: "number" },
    { name: "sick_leave_hours", label: "Sick Leave Hours", type: "number" },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const availability = {
  slug: "availability",
  label: "Availability",
  parent: { resource: "employees" },
  timestampField: null,
  fields: [
    { name: "weekday", label: "Weekday", type: "text" },
    { name: "start_time", label: "Start Time", type: "time" },
    { name: "end_time", label: "End Time", type: "time" },
    { name: "available", label: "Available", type: "boolean", defaultValue: true },
  ],
};

export const shifts = {
  slug: "shifts",
  label: "Shift",
  parent: { resource: "employees" },
  timestampField: "created_at",
  fields: [
    { name: "shift_start", label: "Shift Start", type: "datetime", required: true },
    { name: "shift_end", label: "Shift End", type: "datetime", required: true },
    { name: "role", label: "Role", type: "text" },
    { name: "location", label: "Location", type: "text" },
    {
      name: "status",
      label: "Status",
      type: "enum",
      options: SHIFT_STATUS,
      defaultValue: "Scheduled",
      badgeKind: "shiftStatus",
    },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const timeEntries = {
  slug: "time-entries",
  label: "Time Entry",
  parent: { resource: "employees" },
  timestampField: "created_at",
  fields: [
    {
      name: "shift_id",
      label: "Shift",
      type: "reference",
      reference: { resource: "shifts", scope: "parent", labelFields: ["shift_start", "shift_end"] },
    },
    { name: "clock_in", label: "Clock In", type: "datetime", required: true },
    { name: "clock_out", label: "Clock Out", type: "datetime" },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const payroll = {
  slug: "payroll",
  label: "Payroll Record",
  parent: { resource: "employees" },
  timestampField: "created_at",
  fields: [
    { name: "pay_period_start", label: "Period Start", type: "date", required: true },
    { name: "pay_period_end", label: "Period End", type: "date", required: true },
    { name: "total_hours", label: "Total Hours", type: "number" },
    { name: "hourly_rate", label: "Hourly Rate", type: "number" },
    { name: "gross_pay", label: "Gross Pay", type: "number" },
    { name: "deductions", label: "Deductions", type: "number", defaultValue: 0 },
    { name: "net_pay", label: "Net Pay", type: "number" },
    {
      name: "status",
      label: "Status",
      type: "enum",
      options: PAYROLL_STATUS,
      defaultValue: "Draft",
      badgeKind: "payrollStatus",
    },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const employeeResourceConfigs = [
  supervision,
  registration,
  qualifications,
  performance,
  leave,
  contracts,
  availability,
  shifts,
  timeEntries,
  payroll,
];
