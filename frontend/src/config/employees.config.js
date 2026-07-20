import { EMPLOYEE_ROLE, EMPLOYMENT_STATUS } from "./enums.js";

export const employeesConfig = {
  slug: "employees",
  label: "Employee",
  parent: null,
  timestampField: null,
  fields: [
    { name: "first_name", label: "First Name", type: "text", required: true },
    { name: "last_name", label: "Last Name", type: "text", required: true },
    { name: "email", label: "Email", type: "text" },
    { name: "phone", label: "Phone", type: "text" },
    { name: "role", label: "Role", type: "enum", options: EMPLOYEE_ROLE },
    {
      name: "employment_status",
      label: "Employment Status",
      type: "enum",
      options: EMPLOYMENT_STATUS,
    },
    { name: "hire_date", label: "Hire Date", type: "date" },
    { name: "termination_date", label: "Termination Date", type: "date" },
    { name: "active", label: "Active", type: "boolean", defaultValue: true },
  ],
};
