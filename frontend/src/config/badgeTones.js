export const badgeTones = {
  assignmentType: { Primary: "success", Secondary: "info", Relief: "neutral" },
  accessRole: {
    Admin: "danger",
    Manager: "warning",
    Nurse: "info",
    "Care Worker": "success",
    Family: "neutral",
  },
  auditAction: {
    create: "success",
    update: "info",
    delete: "danger",
    login: "neutral",
    login_failed: "warning",
    password_change: "info",
    access_denied: "danger",
  },
  riskBand: { Low: "success", Medium: "info", High: "warning", Critical: "danger" },
  incidentSeverity: { Low: "success", Medium: "info", High: "warning", Critical: "danger" },
  incidentStatus: {
    Open: "info",
    "Under Review": "warning",
    Reported: "warning",
    Closed: "neutral",
  },
  complaintStatus: {
    Open: "info",
    Investigating: "warning",
    Resolved: "success",
    Closed: "neutral",
  },
  leaveStatus: {
    Pending: "info",
    Approved: "success",
    Rejected: "danger",
    Cancelled: "neutral",
  },
  shiftStatus: {
    Scheduled: "info",
    Confirmed: "info",
    Completed: "success",
    Cancelled: "neutral",
    "No-Show": "danger",
  },
  payrollStatus: { Draft: "neutral", Finalized: "info", Paid: "success" },
  appointmentStatus: {
    Pending: "info",
    Confirmed: "success",
    Cancelled: "neutral",
    Completed: "success",
  },
  verified: { true: "success", false: "warning" },
  conflict: { Conflict: "danger", Available: "success" },
};

export function toneFor(badgeKind, value) {
  if (!badgeKind) return "neutral";
  const map = badgeTones[badgeKind];
  if (!map) return "neutral";
  return map[value] ?? "neutral";
}
