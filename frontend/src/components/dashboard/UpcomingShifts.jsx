import { Link } from "react-router-dom";
import { useAsync } from "../../hooks/useAsync.js";
import { useDirectory, personLabel } from "../../hooks/useDirectory.js";
import { get } from "../../api/client.js";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import EmptyState from "../common/EmptyState.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import { formatRelativeDay } from "../../utils/format.js";
import { IconClock } from "../layout/Icons.jsx";

// Reads the flat GET-only /shifts list (backend/api/v1/parent_scoped_router.py
// only registers GET on the flat path) -- purely for display, never for
// mutation.
export default function UpcomingShifts() {
  const { data, loading, error } = useAsync(() => get("/shifts?skip=0&limit=100"), []);
  const { employeesById } = useDirectory();

  const upcoming = (data || [])
    .filter((s) => ["Scheduled", "Confirmed"].includes(s.status) && new Date(s.shift_start) >= new Date())
    .sort((a, b) => new Date(a.shift_start) - new Date(b.shift_start))
    .slice(0, 8);

  return (
    <section className="card fade-slide-in">
      <h2>Upcoming Shifts</h2>
      <p className="text-muted">Next scheduled or confirmed shifts.</p>
      <ErrorBanner error={error} />
      {loading ? (
        <Skeleton rows={4} />
      ) : !upcoming.length ? (
        <EmptyState message="No upcoming shifts." />
      ) : (
        <ul className="shift-list">
          {upcoming.map((shift) => (
            <li key={shift.id} className="shift-row">
              <div>
                <Link to={`/admin/employees/${shift.employee_id}/shifts`} className="shift-employee">
                  {personLabel(employeesById[shift.employee_id]) || "Unknown"}
                </Link>
                <span className="text-muted"> — {shift.role || "Unassigned role"}</span>
              </div>
              <div className="shift-time">
                <IconClock size={14} />
                {formatRelativeDay(shift.shift_start)}
              </div>
              <StatusBadge value={shift.status} badgeKind="shiftStatus" />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
