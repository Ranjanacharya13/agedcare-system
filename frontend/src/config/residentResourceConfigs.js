import { RISK_LEVEL, ASSISTANCE_LEVEL, INCIDENT_SEVERITY, INCIDENT_STATUS, CARING_ROLES } from "./enums.js";

const employeeRef = {
  type: "reference",
  reference: { resource: "employees", scope: "global", labelFields: ["first_name", "last_name"] },
};

export const behaviour = {
  slug: "behaviour",
  label: "Behaviour Entry",
  parent: { resource: "residents" },
  timestampField: "recorded_at",
  fields: [
    { name: "behaviour", label: "Behaviour", type: "textarea", required: true },
    { name: "trigger", label: "Trigger", type: "text" },
    { name: "intervention", label: "Intervention", type: "textarea" },
    { name: "outcome", label: "Outcome", type: "textarea" },
    { name: "recorded_by", label: "Recorded By", ...employeeRef },
  ],
};

export const medications = {
  slug: "medications",
  label: "Medication",
  parent: { resource: "residents" },
  timestampField: null,
  fields: [
    { name: "medication_name", label: "Medication", type: "text", required: true },
    { name: "dosage", label: "Dosage", type: "text" },
    { name: "frequency", label: "Frequency", type: "text" },
    { name: "route", label: "Route", type: "text" },
    { name: "prescribed_by", label: "Prescribed By", type: "text" },
    { name: "start_date", label: "Start Date", type: "date" },
    { name: "end_date", label: "End Date", type: "date" },
    { name: "active", label: "Active", type: "boolean", defaultValue: true },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const bowelChart = {
  slug: "bowel-chart",
  label: "Bowel Chart Entry",
  parent: { resource: "residents" },
  timestampField: "recorded_at",
  fields: [
    { name: "bowel_type", label: "Bowel Type", type: "text" },
    { name: "consistency", label: "Consistency", type: "text" },
    { name: "notes", label: "Notes", type: "textarea" },
    { name: "recorded_by", label: "Recorded By", ...employeeRef },
  ],
};

export const sleepChart = {
  slug: "sleep-chart",
  label: "Sleep Chart Entry",
  parent: { resource: "residents" },
  timestampField: null,
  fields: [
    { name: "sleep_date", label: "Sleep Date", type: "date" },
    { name: "sleep_start", label: "Sleep Start", type: "time" },
    { name: "wake_time", label: "Wake Time", type: "time" },
    { name: "total_hours", label: "Total Hours", type: "number" },
    { name: "disturbances", label: "Disturbances", type: "textarea" },
    { name: "recorded_by", label: "Recorded By", ...employeeRef },
  ],
};

export const fallRisk = {
  slug: "fall-risk",
  label: "Fall Risk Assessment",
  parent: { resource: "residents" },
  timestampField: null,
  fields: [
    {
      name: "risk_level",
      label: "Risk Level",
      type: "enum",
      options: RISK_LEVEL,
      badgeKind: "riskBand",
    },
    { name: "assessment_date", label: "Assessment Date", type: "date" },
    { name: "assessed_by", label: "Assessed By", ...employeeRef },
    { name: "interventions", label: "Interventions", type: "textarea" },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const assistance = {
  slug: "assistance",
  label: "Assistance Record",
  parent: { resource: "residents" },
  timestampField: "updated_at",
  fields: [
    { name: "assistance_level", label: "Assistance Level", type: "enum", options: ASSISTANCE_LEVEL },
    { name: "mobility", label: "Mobility", type: "text" },
    { name: "transfer_notes", label: "Transfer Notes", type: "textarea" },
    { name: "updated_by", label: "Updated By", ...employeeRef },
  ],
};

export const medicalInventory = {
  slug: "medical-inventory",
  label: "Medical Inventory Item",
  parent: { resource: "residents" },
  timestampField: "created_at",
  fields: [
    { name: "item_name", label: "Item", type: "text", required: true },
    { name: "quantity", label: "Quantity", type: "number", defaultValue: 0 },
    { name: "unit", label: "Unit", type: "text" },
    { name: "expiry_date", label: "Expiry Date", type: "date" },
    { name: "notes", label: "Notes", type: "textarea" },
    { name: "added_by", label: "Added By", ...employeeRef },
  ],
};

export const incidents = {
  slug: "incidents",
  label: "Incident",
  parent: { resource: "residents" },
  timestampField: "created_at",
  fields: [
    { name: "incident_type", label: "Type", type: "text", required: true },
    {
      name: "severity",
      label: "Severity",
      type: "enum",
      required: true,
      options: INCIDENT_SEVERITY,
      badgeKind: "incidentSeverity",
    },
    { name: "description", label: "Description", type: "textarea", required: true },
    { name: "occurred_at", label: "Occurred At", type: "datetime", required: true },
    { name: "location", label: "Location", type: "text" },
    { name: "reported_by", label: "Reported By", ...employeeRef },
    { name: "witnesses", label: "Witnesses", type: "textarea" },
    { name: "immediate_action", label: "Immediate Action", type: "textarea" },
    { name: "is_sirs_reportable", label: "SIRS Reportable", type: "boolean", defaultValue: false },
    { name: "sirs_notified_at", label: "SIRS Notified At", type: "datetime" },
    { name: "sirs_reference_number", label: "SIRS Reference #", type: "text" },
    {
      name: "status",
      label: "Status",
      type: "enum",
      options: INCIDENT_STATUS,
      defaultValue: "Open",
      badgeKind: "incidentStatus",
    },
    { name: "outcome", label: "Outcome", type: "textarea" },
  ],
};

export const medicalHistory = {
  slug: "medical-history",
  label: "Medical History Entry",
  parent: { resource: "residents" },
  timestampField: "recorded_at",
  fields: [
    { name: "diagnosis", label: "Diagnosis", type: "textarea" },
    { name: "allergies", label: "Allergies", type: "textarea" },
    { name: "chronic_conditions", label: "Chronic Conditions", type: "textarea" },
    { name: "surgeries", label: "Surgeries", type: "textarea" },
    { name: "doctor_name", label: "Doctor", type: "text" },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const careVisits = {
  slug: "care-visits",
  label: "Care Schedule",
  parent: { resource: "residents" },
  timestampField: "start_at",
  fields: [
    {
      name: "employee_id",
      label: "Carer",
      type: "reference",
      required: true,
      reference: {
        resource: "employees",
        scope: "global",
        labelFields: ["first_name", "last_name", "role"],
        filter: (e) => e.active !== false && CARING_ROLES.includes(e.role),
      },
    },
    { name: "start_at", label: "From", type: "datetime", required: true },
    { name: "end_at", label: "Until", type: "datetime", required: true },
    { name: "task", label: "Task", type: "text" },
    { name: "notes", label: "Notes", type: "textarea" },
  ],
};

export const residentResourceConfigs = [
  careVisits,
  behaviour,
  medications,
  bowelChart,
  sleepChart,
  fallRisk,
  assistance,
  medicalInventory,
  incidents,
  medicalHistory,
];
