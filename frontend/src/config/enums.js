// Every literal value here must byte-match the backend's StrEnum members
// (backend/models/*.py) -- a mismatch is a silent 422 from Pydantic enum
// validation, not a frontend bug that shows up locally.

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
