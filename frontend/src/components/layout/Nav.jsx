import { NavLink, useNavigate } from "react-router-dom";
import Logo from "./Logo.jsx";
import {
  IconDashboard,
  IconResidents,
  IconEmployees,
  IconComplaints,
  IconCalendar,
  IconPulse,
  IconLogout,
} from "./Icons.jsx";
import { useAsync } from "../../hooks/useAsync.js";
import { getHealth } from "../../api/health.js";
import { useAuth } from "../../context/AuthContext.jsx";

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
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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
      <div className="sidebar-user">
        <span className="sidebar-user-avatar">{(user?.name || "?")[0]}</span>
        <span className="sidebar-user-name">{user?.name || "Staff"}</span>
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
