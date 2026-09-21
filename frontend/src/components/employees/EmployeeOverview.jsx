import { Link } from "react-router-dom";
import { shiftLabel } from "../../hooks/useStaffStatus.js";
import { formatDate } from "../../utils/format.js";

export default function EmployeeOverview({ employee, status, baseUrl }) {
  const facts = [
    ["Role", employee.role || "—"],
    ["Status", employee.employment_status || "—"],
    ["Hired", formatDate(employee.hire_date)],
    ["Residents", status ? status.active_residents : "—"],
    ["Today", status?.shiftsToday.length ? status.shiftsToday.map(shiftLabel).join(", ") : "No shift"],
  ];
  return (
    <div className="overview">
      {status?.reason && <p className="coverage-warning">{status.reason}.</p>}
      <dl className="fact-grid">
        {facts.map(([label, value]) => (
          <div key={label} className="fact">
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <div className="overview-links">
        <Link className="btn btn-secondary btn-sm" to={`${baseUrl}/caseload`}>
          Assigned residents
        </Link>
        <Link className="btn btn-secondary btn-sm" to={`${baseUrl}/shifts`}>
          Shifts
        </Link>
      </div>
    </div>
  );
}
