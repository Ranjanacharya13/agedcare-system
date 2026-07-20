import { COMPLAINT_STATUS } from "./enums.js";

export const complaintsConfig = {
  slug: "complaints",
  label: "Complaint",
  parent: null,
  timestampField: "created_at",
  fields: [
    {
      name: "resident_id",
      label: "Resident",
      type: "reference",
      reference: { resource: "residents", scope: "global", labelFields: ["first_name", "last_name"] },
    },
    {
      name: "employee_id",
      label: "Employee (subject of complaint)",
      type: "reference",
      reference: { resource: "employees", scope: "global", labelFields: ["first_name", "last_name"] },
    },
    { name: "category", label: "Category", type: "text", required: true },
    { name: "description", label: "Description", type: "textarea", required: true },
    { name: "submitted_by_name", label: "Submitted By", type: "text", required: true },
    { name: "submitted_by_relationship", label: "Relationship", type: "text" },
    { name: "submitted_by_contact", label: "Contact Info", type: "text" },
    { name: "is_anonymous", label: "Anonymous", type: "boolean", defaultValue: false },
    {
      name: "status",
      label: "Status",
      type: "enum",
      options: COMPLAINT_STATUS,
      defaultValue: "Open",
      badgeKind: "complaintStatus",
    },
    {
      name: "assigned_to",
      label: "Assigned To",
      type: "reference",
      reference: { resource: "employees", scope: "global", labelFields: ["first_name", "last_name"] },
    },
    { name: "resolution_notes", label: "Resolution Notes", type: "textarea", editOnly: true },
    { name: "resolved_at", label: "Resolved At", type: "datetime", editOnly: true },
  ],
};
