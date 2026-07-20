import { APPOINTMENT_STATUS } from "./enums.js";

const employeeRef = {
  type: "reference",
  reference: { resource: "employees", scope: "global", labelFields: ["first_name", "last_name"] },
};

// Shared with the public intake form (frontend/src/pages/PublicLandingPage.jsx),
// which renders a hand-picked subset of these fields directly rather than
// going through ResourcePanel -- a visitor needs a one-shot form, not a data
// table. Keep this as the single source of truth for field labels/options so
// the two surfaces don't drift.
export const appointmentsConfig = {
  slug: "appointments",
  label: "Appointment",
  parent: null,
  timestampField: "created_at",
  fields: [
    { name: "full_name", label: "Full Name", type: "text", required: true },
    { name: "email", label: "Email", type: "text", required: true },
    { name: "phone", label: "Phone", type: "text" },
    { name: "appointment_type", label: "Appointment Type", type: "text", required: true },
    { name: "preferred_date", label: "Preferred Date", type: "date" },
    { name: "preferred_time", label: "Preferred Time", type: "time" },
    { name: "message", label: "Message", type: "textarea" },
    {
      name: "status",
      label: "Status",
      type: "enum",
      options: APPOINTMENT_STATUS,
      defaultValue: "Pending",
      badgeKind: "appointmentStatus",
      editOnly: true,
    },
    { name: "scheduled_at", label: "Scheduled At", type: "datetime", editOnly: true },
    { name: "handled_by", label: "Handled By", ...employeeRef, editOnly: true },
    { name: "admin_notes", label: "Admin Notes", type: "textarea", editOnly: true },
  ],
};
