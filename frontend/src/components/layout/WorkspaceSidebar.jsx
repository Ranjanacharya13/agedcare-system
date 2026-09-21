import { NavLink } from "react-router-dom";

/** Secondary sidebar for a single person's workspace (resident or employee).
 *  Tinted by `tone`; the main nav is hidden while one is open (see AppShell). */
export default function WorkspaceSidebar({
  tone,
  backTo,
  backLabel,
  avatar,
  title,
  subtitle,
  pill,
  groups,
  baseUrl,
  activeKey,
}) {
  return (
    <aside className={`resident-sidebar tone-${tone}`} aria-label="Sections">
      <NavLink to={backTo} className="resident-sidebar-back">
        <span aria-hidden="true">←</span> {backLabel}
      </NavLink>
      <NavLink to="/admin" className="resident-sidebar-home">
        Dashboard
      </NavLink>

      <div className="resident-sidebar-id">
        <span className="resident-card-avatar" aria-hidden="true">
          {avatar}
        </span>
        <span>
          <strong>{title}</strong>
          <small>{subtitle}</small>
        </span>
      </div>
      {pill && <span className="tone-pill resident-sidebar-pill">{pill}</span>}

      <nav>
        {groups.map((group) => (
          <div key={group.title} className="resident-sidebar-group">
            <p className="resident-sidebar-heading">{group.title}</p>
            {group.items.map((item) => (
              <NavLink
                key={item.key}
                to={item.key === "overview" ? baseUrl : `${baseUrl}/${item.key}`}
                end
                className={`resident-sidebar-link${activeKey === item.key ? " is-active" : ""}`}
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  );
}
