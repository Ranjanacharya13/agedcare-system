import { get, post, patch } from "./client.js";
import { localDateString } from "../utils/format.js";

/** Care visits overlapping [start, end): who is with which resident, hour by hour. */
export const getCareSchedule = (start, end, options) =>
  get(`/care-schedule?start=${encodeURIComponent(start.toISOString())}&end=${encodeURIComponent(end.toISOString())}`, options);

/** Book the carer's next free hour on shift today with this resident; null if none left. */
export const bookNextFreeHour = (residentId, employeeId, [dayStart, dayEnd], options) =>
  post(
    `/residents/${residentId}/care-visits/next-free-hour`,
    { employee_id: employeeId, day_start: dayStart.toISOString(), day_end: dayEnd.toISOString() },
    options
  );

/** Every active staff member with their current load and a light/steady/packed level. */
export const getStaffWorkload = (options) => get("/staff-workload", options);

export const reassignCarer = (residentId, assignmentId, body, options) =>
  post(`/residents/${residentId}/assignments/${assignmentId}/reassign`, body, options);

/** Close an assignment (kept as history rather than deleted). */
export const endAssignment = (residentId, assignmentId, options) =>
  patch(
    `/residents/${residentId}/assignments/${assignmentId}`,
    { end_date: localDateString(), active: false },
    options
  );

export const changeAssignmentType = (residentId, assignmentId, assignment_type, options) =>
  patch(`/residents/${residentId}/assignments/${assignmentId}`, { assignment_type }, options);

/** Who cares for this resident, and which of them is on shift right now. */
export const getCareTeam = (residentId, options) =>
  get(`/residents/${residentId}/care-team`, options);

/** Which residents this employee is responsible for, riskiest first. */
export const getCaseload = (employeeId, options) =>
  get(`/employees/${employeeId}/caseload`, options);

export const getCoverageReport = (options) => get("/coverage", options);

/** Confirm several assignments at once — where a reviewed plan becomes real.
 *  Resolves even when some lines were rejected: the body names which. */
export const createAssignmentsInBulk = (assignments, options) =>
  post("/coverage/assignments", { assignments }, options);

export const createAssignment = (residentId, body, options) =>
  post(`/residents/${residentId}/assignments`, body, options);

/** End every active assignment, facility-wide. Kept as history, not deleted. */
export const endAllAssignments = (options) => post("/coverage/assignments/end-all", {}, options);
