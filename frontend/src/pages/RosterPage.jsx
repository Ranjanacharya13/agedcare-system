import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAsync } from "../hooks/useAsync.js";
import { useAuth } from "../context/AuthContext.jsx";
import { useDirectory } from "../hooks/useDirectory.js";
import { dayBounds } from "../hooks/useStaffStatus.js";
import { createResourceApi } from "../api/resourceApi.js";
import { shifts as shiftsConfig } from "../config/employeeResourceConfigs.js";
import Table from "../components/common/Table.jsx";
import StatusBadge from "../components/common/StatusBadge.jsx";
import Button from "../components/common/Button.jsx";
import Modal from "../components/common/Modal.jsx";
import ResourceForm from "../components/resource/ResourceForm.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import { formatDateTime } from "../utils/format.js";

const shiftsApi = createResourceApi(shiftsConfig);

// Same shift fields as the per-employee Shifts tab, plus an employee picker up
// front — the only thing that tab doesn't need, since it already has a parent.
const shiftFormResource = {
  ...shiftsConfig,
  fields: [
    {
      name: "employee_id",
      label: "Employee",
      type: "reference",
      required: true,
      reference: { resource: "employees", scope: "global", labelFields: ["first_name", "last_name"] },
    },
    ...shiftsConfig.fields,
  ],
};

export default function RosterPage() {
  const navigate = useNavigate();
  const { can } = useAuth();
  const { employeesById } = useDirectory();
  const [version, setVersion] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [day, setDay] = useState(() => new Date());

  const load = useCallback(
    (signal) => shiftsApi.list({ limit: 500, signal }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [version]
  );
  const { data, loading, error } = useAsync(load, [load]);

  const [dayStart, dayEnd] = dayBounds(day);
  const dayShifts = useMemo(
    () =>
      (data || []).filter(
        (s) => new Date(s.shift_start) < dayEnd && new Date(s.shift_end) > dayStart
      ),
    [data, dayStart, dayEnd]
  );
  const moveDay = (n) => setDay((d) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n));

  const handleCreate = async (values) => {
    const { employee_id, ...shift } = values;
    await shiftsApi.create(shift, { parentId: employee_id });
    setShowForm(false);
    setVersion((v) => v + 1);
  };

  const columns = [
    {
      key: "employee",
      label: "Employee",
      render: (row) => {
        const employee = employeesById[row.employee_id];
        return employee ? `${employee.first_name} ${employee.last_name}` : "—";
      },
    },
    {
      key: "when",
      label: "When",
      render: (row) => `${formatDateTime(row.shift_start)} – ${formatDateTime(row.shift_end)}`,
    },
    { key: "role", label: "Role", render: (row) => row.role || <span className="text-muted">—</span> },
    { key: "location", label: "Location", render: (row) => row.location || <span className="text-muted">—</span> },
    { key: "status", label: "Status", render: (row) => <StatusBadge value={row.status} badgeKind="shiftStatus" /> },
  ];

  return (
    <div className="page">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "var(--space-4)" }}>
        <div>
          <h1 className="page-title">Shifts</h1>
          <p className="text-muted page-intro">
            Every rostered shift, across every staff member. Add one here for anyone, or from
            that staff member&rsquo;s own Shifts tab.
          </p>
        </div>
        {can("employee_roster", "write") && (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            + Add Shift
          </Button>
        )}
      </div>

      <div className="day-cal-nav" style={{ margin: "var(--space-4) 0" }}>
        <button type="button" onClick={() => moveDay(-1)} aria-label="Previous day">‹</button>
        <strong>{day.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "short" })}</strong>
        <button type="button" onClick={() => moveDay(1)} aria-label="Next day">›</button>
        <button type="button" onClick={() => setDay(new Date())}>Today</button>
      </div>

      <ErrorBanner error={error} />
      {loading || !data ? (
        <Skeleton rows={6} />
      ) : dayShifts.length ? (
        <Table
          columns={columns}
          rows={dayShifts}
          onRowClick={(row) => navigate(`/admin/employees/${row.employee_id}/shifts`)}
          emptyMessage="No shifts this day."
        />
      ) : (
        <EmptyState title="No shifts this day" message="Add one for this date, or pick another day." />
      )}

      {showForm && (
        <Modal title="Add Shift" onClose={() => setShowForm(false)}>
          <ResourceForm
            resource={shiftFormResource}
            record={null}
            onSubmit={handleCreate}
            onCancel={() => setShowForm(false)}
          />
        </Modal>
      )}
    </div>
  );
}
