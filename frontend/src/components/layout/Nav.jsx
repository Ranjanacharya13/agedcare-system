import { NavLink, useNavigate } from "react-router-dom";
import Logo from "./Logo.jsx";
import {
  IconDashboard,
  IconResidents,
  IconEmployees,
  IconComplaints,
  IconCalendar,
  IconClock,
  IconPulse,
  IconAlert,
  IconLogout,
} from "./Icons.jsx";
import { useAsync } from "../../hooks/useAsync.js";
import { getHealth } from "../../api/health.js";
import { useAuth } from "../../context/AuthContext.jsx";

const links = [
  { to: "/admin", label: "Dashboard", end: true, Icon: IconDashboard },
  { to: "/admin/residents", label: "Residents", Icon: IconResidents, group: "residents" },
  { to: "/admin/employees", label: "Staff (HR)", Icon: IconEmployees, group: "employees" },
  { to: "/admin/coverage", label: "Coverage", Icon: IconResidents, group: "assignments" },
  { to: "/admin/roster", label: "Shifts", Icon: IconClock, group: "employee_roster" },
  { to: "/admin/appointments", label: "Appointments", Icon: IconCalendar, group: "appointments" },
  { to: "/admin/complaints", label: "Complaints", Icon: IconComplaints, group: "complaints" },
  { to: "/admin/audit-log", label: "Audit Log", Icon: IconAlert, group: "audit" },
  { to: "/admin/users", label: "Login Accounts", Icon: IconLogout, group: "users" },
];

export default function Nav() {
  const { data, error } = useAsync(() => getHealth(), []);
  const connected = Boolean(data?.status === "ok") && !error;
  const { displayName, role, logout, can } = useAuth();
  const navigate = useNavigate();

  const visibleLinks = links.filter((link) => !link.group || can(link.group, "read"));

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="app-sidebar">
      <div className="app-sidebar-brand">
        <Logo tone="dark" />
      </div>
      <nav className="app-nav-links">
        {visibleLinks.map(({ to, label, end, Icon }) => (
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
      <div className="sidebar-user">
        <span className="sidebar-user-avatar">{(displayName || "?")[0].toUpperCase()}</span>
        <span className="sidebar-user-name">
          {displayName}
          {role && <small className="sidebar-user-role">{role}</small>}
        </span>
        <button
          type="button"
          className="sidebar-logout-btn"
          onClick={handleLogout}
          title="Sign out"
          aria-label="Sign out"
        >
          <IconLogout size={16} />
        </button>
      </div>
      <div className="app-sidebar-footer">
        <span className={`status-dot ${connected ? "status-dot-on" : "status-dot-off"}`} />
        <IconPulse size={16} />
        <span>{connected ? "Backend connected" : "Backend unreachable"}</span>
      </div>
    </aside>
  );
}
