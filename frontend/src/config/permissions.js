export const ACCESS_ROLES = {
  ADMIN: "Admin",
  MANAGER: "Manager",
  NURSE: "Nurse",
  CARE_WORKER: "Care Worker",
  FAMILY: "Family",
};

const { ADMIN, MANAGER, NURSE, CARE_WORKER } = ACCESS_ROLES;

const ALL_STAFF = [ADMIN, MANAGER, NURSE, CARE_WORKER];
const CLINICAL_STAFF = [ADMIN, MANAGER, NURSE];
const LEADERSHIP = [ADMIN, MANAGER];
const ADMIN_ONLY = [ADMIN];

export const PERMISSIONS = {
  residents: { read: ALL_STAFF, write: CLINICAL_STAFF },
  resident_charts: { read: ALL_STAFF, write: ALL_STAFF },
  resident_clinical: { read: ALL_STAFF, write: CLINICAL_STAFF },
  employees: { read: ALL_STAFF, write: LEADERSHIP },
  // Who cares for whom. All staff read it; nurses and leadership decide it.
  assignments: { read: ALL_STAFF, write: CLINICAL_STAFF },
  employee_roster: { read: ALL_STAFF, write: LEADERSHIP },
  employee_hr: { read: LEADERSHIP, write: LEADERSHIP },
  complaints: { read: LEADERSHIP, write: LEADERSHIP },
  appointments: { read: ALL_STAFF, write: LEADERSHIP },
  analytics: { read: ALL_STAFF, write: [] },
  roster_planning: { read: ALL_STAFF, write: LEADERSHIP },
  users: { read: ADMIN_ONLY, write: ADMIN_ONLY },
  audit: { read: LEADERSHIP, write: [] },
};

export function can(role, group, action = "read") {
  if (!role) return false;
  return (PERMISSIONS[group]?.[action] ?? []).includes(role);
}
