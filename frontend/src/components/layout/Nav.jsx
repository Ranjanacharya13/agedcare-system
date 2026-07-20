import { NavLink } from "react-router-dom";
import Logo from "./Logo.jsx";
import {
  IconDashboard,
  IconResidents,
  IconEmployees,
  IconComplaints,
  IconCalendar,
  IconPulse,
} from "./Icons.jsx";
import { useAsync } from "../../hooks/useAsync.js";
import { getHealth } from "../../api/health.js";

const links = [
  { to: "/admin", label: "Dashboard", end: true, Icon: IconDashboard },
  { to: "/admin/residents", label: "Residents", Icon: IconResidents },
  { to: "/admin/employees", label: "Employees", Icon: IconEmployees },
  { to: "/admin/appointments", label: "Appointments", Icon: IconCalendar },
  { to: "/admin/complaints", label: "Complaints", Icon: IconComplaints },
];

export default function Nav() {
  const { data, error } = useAsync(() => getHealth(), []);
  const connected = Boolean(data?.status === "ok") && !error;

  return (
    <aside className="app-sidebar">
      <div className="app-sidebar-brand">
        <Logo tone="dark" />
      </div>
      <nav className="app-nav-links">
        {links.map(({ to, label, end, Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `app-nav-link ${isActive ? "app-nav-link-active" : ""}`}
          >
            <Icon size={19} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="app-sidebar-footer">
        <span className={`status-dot ${connected ? "status-dot-on" : "status-dot-off"}`} />
        <IconPulse size={16} />
        <span>{connected ? "Backend connected" : "Backend unreachable"}</span>
      </div>
    </aside>
  );
}
