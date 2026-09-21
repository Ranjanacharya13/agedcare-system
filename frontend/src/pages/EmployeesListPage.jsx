import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApiResource } from "../hooks/useApiResource.js";
import { shiftLabel, useStaffStatus } from "../hooks/useStaffStatus.js";
import { useAuth } from "../context/AuthContext.jsx";
import { employeesConfig } from "../config/employees.config.js";
import ResourceForm from "../components/resource/ResourceForm.jsx";
import Modal from "../components/common/Modal.jsx";
import Button from "../components/common/Button.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import { initials } from "../utils/format.js";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "available", label: "Available" },
  { key: "unavailable", label: "No shift / unassigned" },
];

/** Staff cards. Light blue = on shift today with residents to look after;
 *  light red = no shift today or nobody assigned (the card says which). */
export default function EmployeesListPage() {
  const navigate = useNavigate();
  const { can } = useAuth();
  const { items, loading, error, create } = useApiResource(employeesConfig);
  const { byId } = useStaffStatus();
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);

  const toneOf = (e) => byId[e.id]?.tone || "available";
  const counts = {
    all: items.length,
    available: items.filter((e) => toneOf(e) === "available").length,
    unavailable: items.filter((e) => toneOf(e) === "unavailable").length,
  };
  const q = query.trim().toLowerCase();
  const visible = items
    .filter((e) => filter === "all" || toneOf(e) === filter)
    .filter((e) => !q || `${e.first_name} ${e.last_name} ${e.role || ""}`.toLowerCase().includes(q))
    .sort((a, b) => `${a.last_name}${a.first_name}`.localeCompare(`${b.last_name}${b.first_name}`));

  return (
    <div className="page">
      <div className="residents-head">
        <h1 className="page-title">Staff</h1>
        {can("employees", "write") && (
          <Button size="sm" onClick={() => setShowForm(true)}>
            + Add Employee
          </Button>
        )}
      </div>
      <p className="text-muted page-intro">
        <span className="tone-dot tone-available" /> on shift today with residents assigned &nbsp;
        <span className="tone-dot tone-unavailable" /> no shift today, or no residents assigned.
        Login accounts are managed separately under <strong>Login Accounts</strong>.
      </p>

      <div className="residents-toolbar">
        <input
          type="search"
          className="residents-search"
          placeholder="Search by name or role"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Search staff"
        />
        <div className="filter-chips" role="group" aria-label="Filter staff">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              type="button"
              className={`filter-chip filter-${f.key}${filter === f.key ? " is-active" : ""}`}
              onClick={() => setFilter(f.key)}
              aria-pressed={filter === f.key}
            >
              {f.key !== "all" && <span className={`tone-dot tone-${f.key}`} aria-hidden="true" />}
              {f.label} <span className="filter-count">{counts[f.key]}</span>
            </button>
          ))}
        </div>
      </div>

      <ErrorBanner error={error} />

      {loading ? (
        <Skeleton rows={4} />
      ) : visible.length === 0 ? (
        <p className="text-muted">No staff match.</p>
      ) : (
        <ul className="resident-grid">
          {visible.map((e) => {
            const st = byId[e.id];
            return (
              <li key={e.id}>
                <button
                  type="button"
                  className={`resident-card tone-${toneOf(e)}${e.active === false ? " is-inactive" : ""}`}
                  onClick={() => navigate(`/admin/employees/${e.id}`)}
                >
                  <span className="resident-card-avatar" aria-hidden="true">
                    {initials(e.first_name, e.last_name)}
                  </span>
                  <span className="resident-card-main">
                    <strong>
                      {e.first_name} {e.last_name}
                    </strong>
                    <small>{e.role || "Role not set"}</small>
                    <span className="resident-card-tags">
                      <span className="tone-pill">
                        {st?.reason ||
                          (st?.shiftsToday[0] ? `On shift ${shiftLabel(st.shiftsToday[0])}` : "Available")}
                      </span>
                    </span>
                  </span>
                  <span className="resident-card-room">
                    <small>Residents</small>
                    <strong>{st?.active_residents ?? "—"}</strong>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {showForm && (
        <Modal title="Add Employee" onClose={() => setShowForm(false)}>
          <ResourceForm
            resource={employeesConfig}
            record={null}
            onSubmit={async (values) => {
              await create(values);
              setShowForm(false);
            }}
            onCancel={() => setShowForm(false)}
          />
        </Modal>
      )}
    </div>
  );
}
