import { ACCESS_ROLE } from "./enums.js";

export const usersConfig = {
  slug: "users",
  label: "Account",
  parent: null,
  timestampField: null,
  fields: [
    { name: "email", label: "Email", type: "text", required: true },
    { name: "full_name", label: "Full Name", type: "text" },
    {
      name: "access_role",
      label: "Access Role",
      type: "enum",
      options: ACCESS_ROLE,
      required: true,
      badgeKind: "accessRole",
    },
    {
      name: "password",
      label: "Initial Password (at least 12 characters)",
      type: "text",
      required: true,
      createOnly: true,
      showInTable: false,
    },
    { name: "active", label: "Active", type: "boolean", defaultValue: true },
    { name: "last_login_at", label: "Last Sign-In", type: "datetime", readOnly: true },
  ],
};
