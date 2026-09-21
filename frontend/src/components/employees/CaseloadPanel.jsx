import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAsync } from "../../hooks/useAsync.js";
import { getCaseload } from "../../api/assignments.js";
import Table from "../common/Table.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import EmptyState from "../common/EmptyState.jsx";

export default function CaseloadPanel({ employeeId }) {
  const navigate = useNavigate();
  const load = useCallback((signal) => getCaseload(employeeId, { signal }), [employeeId]);
  const { data, loading, error } = useAsync(load, [load]);

  if (loading) return <Skeleton rows={4} />;
  if (error) return <ErrorBanner error={error} />;
  if (!data) return null;

  const active = data.residents.filter((r) => r.active);

  const columns = [
    {
      key: "name",
      label: "Resident",
      render: (row) => (
        <span>
          {row.first_name} {row.last_name}
          {row.room_number && <small className="algo-subtle">Room {row.room_number}</small>}
        </span>
      ),
    },
    {
      key: "assignment_type",
      label: "Role",
      render: (row) => (
        <StatusBadge value={row.assignment_type} badgeKind="assignmentType" />
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (row) =>
        row.active ? (
          <span className="text-muted">Active</span>
        ) : (
          <span className="text-muted">Ended</span>
        ),
    },
  ];

  if (!data.residents.length) {
    return (
      <EmptyState
        title="No residents assigned"
        message="Assign this staff member from a resident's Care Team tab."
      />
    );
  }

  return (
    <div className="caseload">
      <div className="algo-stat-row">
        <div className="algo-stat">
          <span className="algo-stat-label">Residents assigned</span>
          <span className="algo-stat-value">{active.length}</span>
        </div>
        <div className="algo-stat">
          <span className="algo-stat-label">As primary carer</span>
          <span className="algo-stat-value">{data.primary_count}</span>
        </div>
        <div className="algo-stat">
          <span className="algo-stat-label">Hours this week</span>
          <span className="algo-stat-value">{data.hours_this_week}</span>
        </div>
      </div>

      <Table
        columns={columns}
        rows={data.residents}
        rowKey="assignment_id"
        onRowClick={(row) => navigate(`/admin/residents/${row.resident_id}`)}
        emptyMessage="No residents assigned."
      />
    </div>
  );
}
