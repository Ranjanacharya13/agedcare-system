import { COGNITIVE_STATUS } from "./enums.js";

export const residentsConfig = {
  slug: "residents",
  label: "Resident",
  parent: null,
  timestampField: null,
  fields: [
    { name: "first_name", label: "First Name", type: "text", required: true },
    { name: "last_name", label: "Last Name", type: "text", required: true },
    { name: "dob", label: "Date of Birth", type: "date" },
    { name: "gender", label: "Gender", type: "text" },
    {
      name: "cognitive_status",
      label: "Cognitive Status",
      type: "enum",
      options: COGNITIVE_STATUS,
    },
    { name: "room_number", label: "Room", type: "text" },
    { name: "admission_date", label: "Admission Date", type: "date" },
    { name: "active", label: "Active", type: "boolean", defaultValue: true },
    {
      name: "emergency_contact",
      label: "Emergency Contact",
      type: "group",
      showInTable: false,
      fields: [
        { name: "name", label: "Contact Name", type: "text", required: true },
        { name: "relationship", label: "Relationship", type: "text" },
        { name: "phone", label: "Phone", type: "text" },
        { name: "email", label: "Email", type: "text" },
      ],
    },
  ],
};
