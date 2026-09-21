import { useMemo, useState } from "react";
import { shiftLabel, useStaffStatus } from "../../hooks/useStaffStatus.js";
import Modal from "../common/Modal.jsx";
import Button from "../common/Button.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import { ASSIGNMENT_TYPE } from "../../config/enums.js";
import { initials } from "../../utils/format.js";

const LEVEL_LABEL = { light: "Light load", steady: "Steady", packed: "Packed" };

export default function CarerPicker({
  mode,
  currentMember,
  takenEmployeeIds,
  hasPrimary,
  onConfirm,
  onClose,
}) {
  const { staff: allStaff, byId, loading, error } = useStaffStatus();
  const data = allStaff.length || !loading ? { staff: allStaff, average_residents: allStaff.length ? +(allStaff.reduce((n, s) => n + s.active_residents, 0) / allStaff.length).toFixed(1) : 0 } : null;
  const [onShiftOnly, setOnShiftOnly] = useState(false);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(null);
  const [type, setType] = useState(hasPrimary ? "Secondary" : "Primary");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  const staff = useMemo(() => {
    const q = query.trim().toLowerCase();
    const onShift = (s) => (byId[s.employee_id]?.shiftsToday.length ? 0 : 1);
    return (data?.staff || [])
      .filter((s) => !q || `${s.first_name} ${s.last_name} ${s.role || ""}`.toLowerCase().includes(q))
      .filter((s) => !onShiftOnly || onShift(s) === 0)
      .sort((a, b) => onShift(a) - onShift(b)); // stable: keeps lightest-load order within each group
  }, [data, query, byId, onShiftOnly]);

  const confirm = async () => {
    setSaving(true);
    setSaveError(null);
    try {
      await onConfirm(selected, type);
    } catch (err) {
      setSaveError(err);
      setSaving(false);
    }
  };

  const title =
    mode === "reassign"
      ? `Reassign ${currentMember.first_name} ${currentMember.last_name}'s place`
      : "Add a carer";

  const chosen = data?.staff.find((s) => s.employee_id === selected);

  return (
    <Modal
      title={title}
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={confirm} disabled={!selected || saving}>
            {saving
              ? "Saving…"
              : chosen
                ? mode === "reassign"
                  ? `Hand over to ${chosen.first_name}`
                  : `Add ${chosen.first_name}`
                : "Choose a carer"}
          </Button>
        </>
      }
    >
      {mode === "reassign" && (
        <p className="text-muted picker-lead">
          {currentMember.first_name} stays on record as the previous {currentMember.assignment_type.toLowerCase()}{" "}
          carer (their place ends today). The new carer starts today in the same role.
        </p>
      )}

      {mode === "add" && (
        <label className="picker-type">
          Role on care team
          <select value={type} onChange={(e) => setType(e.target.value)}>
            {ASSIGNMENT_TYPE.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
      )}

      <label className="picker-type">
        <span>
          <input type="checkbox" checked={onShiftOnly} onChange={(e) => setOnShiftOnly(e.target.checked)} /> Only staff
          on shift today
        </span>
      </label>

      <input
        className="picker-search"
        type="search"
        placeholder="Search staff by name or role"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search staff"
      />

      <ErrorBanner error={error || saveError} />
      {loading && <Skeleton rows={4} />}

      {data && (
        <ul className="picker-list" role="listbox" aria-label="Staff on shift first, then lightest workload">
          {staff.map((s) => {
            const taken = takenEmployeeIds.has(s.employee_id);
            const isCurrent = currentMember?.employee_id === s.employee_id;
            return (
              <li key={s.employee_id}>
                <button
                  type="button"
                  role="option"
                  aria-selected={selected === s.employee_id}
                  disabled={taken}
                  className={`picker-row picker-${s.level}${selected === s.employee_id ? " is-selected" : ""}`}
                  onClick={() => setSelected(s.employee_id)}
                >
                  <span className="care-team-avatar" aria-hidden="true">
                    {initials(s.first_name, s.last_name)}
                  </span>
                  <span className="picker-who">
                    <strong>
                      {s.first_name} {s.last_name}
                    </strong>
                    <small>{s.role || "Role not set"}</small>
                    {byId[s.employee_id]?.shiftsToday.length ? (
                      <span className="picker-shift on">On shift {shiftLabel(byId[s.employee_id].shiftsToday[0])}</span>
                    ) : (
                      <span className="picker-shift off">No shift today</span>
                    )}
                  </span>
                  <span className="picker-load">
                    <span className={`load-chip load-${s.level}`}>{LEVEL_LABEL[s.level]}</span>
                    <small>
                      {s.active_residents} resident{s.active_residents === 1 ? "" : "s"}
                      {s.primary_count > 0 && ` · ${s.primary_count} as primary`}
                    </small>
                  </span>
                  {taken && (
                    <span className="picker-note">{isCurrent ? "Current carer" : "Already on team"}</span>
                  )}
                </button>
              </li>
            );
          })}
          {staff.length === 0 && <li className="text-muted">No staff match that search.</li>}
        </ul>
      )}

      {chosen?.level === "packed" && (
        <p className="coverage-warning" role="status">
          {chosen.first_name} is already carrying {chosen.active_residents} residents (facility
          average {data.average_residents}). You can still choose them, but a lighter option is
          listed higher up.
        </p>
      )}
    </Modal>
  );
}
