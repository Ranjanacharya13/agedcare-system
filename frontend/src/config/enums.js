export const COGNITIVE_STATUS = [
  "Cognitive",
  "Non-Cognitive",
  "Disabled-Cognitive",
  "Disabled-Non-Cognitive",
];

export const EMPLOYEE_ROLE = [
  "Care Planner",
  "Care Coordinator",
  "Registered Nurse",
  "Kitchen Staff",
  "Laundry Staff",
  "Administrator",
  "Manager",
];

/** Mirrors backend CARING_ROLES: the only job titles that may be put with a resident. */
export const CARING_ROLES = ["Registered Nurse", "Care Planner", "Care Coordinator"];

export const EMPLOYMENT_STATUS = ["Full-Time", "Part-Time", "Casual", "Agency"];

export const RISK_LEVEL = ["Low", "Medium", "High"];

export const ASSISTANCE_LEVEL = ["Independent", "Single Assist", "Double Assist"];

export const INCIDENT_SEVERITY = ["Low", "Medium", "High", "Critical"];

export const INCIDENT_STATUS = ["Open", "Under Review", "Reported", "Closed"];

export const LEAVE_STATUS = ["Pending", "Approved", "Rejected", "Cancelled"];

export const SHIFT_STATUS = ["Scheduled", "Confirmed", "Completed", "Cancelled", "No-Show"];

export const PAYROLL_STATUS = ["Draft", "Finalized", "Paid"];

export const COMPLAINT_STATUS = ["Open", "Investigating", "Resolved", "Closed"];

export const APPOINTMENT_STATUS = ["Pending", "Confirmed", "Cancelled", "Completed"];

export const ACCESS_ROLE = ["Admin", "Manager", "Nurse", "Care Worker", "Family"];

// Audit actions (backend/models/audit_log.py AuditAction).
export const AUDIT_ACTION = [
  "create",
  "update",
  "delete",
  "login",
  "login_failed",
  "password_change",
  "access_denied",
];

// Care team roles (backend/models/resident_assignment.py AssignmentType).
export const ASSIGNMENT_TYPE = ["Primary", "Secondary", "Relief"];
