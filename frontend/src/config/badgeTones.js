// Maps enum literal values onto one of 5 semantic tones (not one CSS color
// per literal -- ~30 literals across 8 enums would otherwise demand 30
// custom properties). StatusBadge looks up value -> tone -> CSS vars.

export const badgeTones = {
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
