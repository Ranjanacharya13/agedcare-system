import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApiResource } from "../hooks/useApiResource.js";
import { useAuth } from "../context/AuthContext.jsx";
import { residentsConfig } from "../config/residents.config.js";
import ResourceForm from "../components/resource/ResourceForm.jsx";
import Modal from "../components/common/Modal.jsx";
import Button from "../components/common/Button.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import { ageFromDob, isDisabledStatus, residentTone } from "../utils/residentTone.js";
import { initials } from "../utils/format.js";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "cognitive", label: "Cognitive" },
  { key: "non-cognitive", label: "Non-cognitive" },
];

export default function ResidentsListPage() {
  const navigate = useNavigate();
  const { can } = useAuth();
  const { items, loading, error, create } = useApiResource(residentsConfig);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);

  const counts = useMemo(
    () => ({
      all: items.length,
      cognitive: items.filter((r) => residentTone(r.cognitive_status) === "cognitive").length,
      "non-cognitive": items.filter((r) => residentTone(r.cognitive_status) === "non-cognitive")
        .length,
    }),
    [items]
  );

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items
      .filter((r) => filter === "all" || residentTone(r.cognitive_status) === filter)
      .filter(
        (r) =>
          !q || `${r.first_name} ${r.last_name} ${r.room_number || ""}`.toLowerCase().includes(q)
      )
      .sort((a, b) => `${a.last_name}${a.first_name}`.localeCompare(`${b.last_name}${b.first_name}`));
  }, [items, query, filter]);

  return (
    <div className="page">
      <div className="residents-head">
        <h1 className="page-title">Residents</h1>
        {can("residents", "write") && (
          <Button size="sm" onClick={() => setShowForm(true)}>
            + Add Resident
          </Button>
        )}
      </div>

      <div className="residents-toolbar">
        <input
          type="search"
          className="residents-search"
          placeholder="Search by name or room"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Search residents"
        />
        <div className="filter-chips" role="group" aria-label="Filter by cognitive status">
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
        <p className="text-muted">No residents match.</p>
      ) : (
        <ul className="resident-grid">
          {visible.map((r) => {
            const tone = residentTone(r.cognitive_status);
            const age = ageFromDob(r.dob);
            return (
              <li key={r.id}>
                <button
                  type="button"
                  className={`resident-card tone-${tone}${r.active === false ? " is-inactive" : ""}`}
                  onClick={() => navigate(`/admin/residents/${r.id}`)}
                >
                  <span className="resident-card-avatar" aria-hidden="true">
                    {initials(r.first_name, r.last_name)}
                  </span>
                  <span className="resident-card-main">
                    <strong>
                      {r.first_name} {r.last_name}
                    </strong>
                    <small>
                      {age !== null ? `${age} yrs` : "Age unknown"}
                      {r.gender ? ` · ${r.gender}` : ""}
                    </small>
                    <span className="resident-card-tags">
                      <span className="tone-pill">{r.cognitive_status || "Not classified"}</span>
                      {isDisabledStatus(r.cognitive_status) && (
                        <span className="tone-pill tone-pill-outline">Disability</span>
                      )}
                      {r.active === false && <span className="tone-pill tone-pill-outline">Inactive</span>}
                    </span>
                  </span>
                  <span className="resident-card-room">
                    <small>Room</small>
                    <strong>{r.room_number || "—"}</strong>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {showForm && (
        <Modal title="Add Resident" onClose={() => setShowForm(false)}>
          <ResourceForm
            resource={residentsConfig}
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
