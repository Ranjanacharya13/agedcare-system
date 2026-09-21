import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAsync } from "../hooks/useAsync.js";
import { getCoverageReport } from "../api/assignments.js";
import Table from "../components/common/Table.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import AllocationPlan, { ApplyResult } from "../components/coverage/AllocationPlan.jsx";

export default function CoveragePage() {
  const navigate = useNavigate();
  const [version, setVersion] = useState(0);
  const [applied, setApplied] = useState(null);
  const load = useCallback(
    (signal) => getCoverageReport({ signal }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [version]
  );
  const { data, loading, error } = useAsync(load, [load]);

  if (loading) return <Skeleton rows={6} />;
  if (error) return <ErrorBanner error={error} />;
  if (!data) return null;

  const coverage =
    data.total_residents > 0
      ? Math.round((data.residents_with_primary / data.total_residents) * 100)
      : 100;

  const unassignedColumns = [
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
      key: "gap",
      label: "Gap",
      render: (row) =>
        row.has_any_carer ? (
          <span className="text-muted">Has carers, but no named primary</span>
        ) : (
          <span className="coverage-critical">No carer at all</span>
        ),
    },
  ];

  const staffColumns = [
    {
      key: "name",
      label: "Staff member",
      render: (row) => `${row.first_name} ${row.last_name}`,
    },
    {
      key: "role",
      label: "Role",
      render: (row) => row.role || <span className="text-muted">—</span>,
    },
  ];

  return (
    <div className="page">
      <h1 className="page-title">Coverage</h1>
      <p className="text-muted page-intro">
        Every resident should have one named primary carer &mdash; a key worker who knows them
        and is the family&rsquo;s point of contact. This page shows where that is missing, and
        which staff are carrying no residents.
      </p>

      <div className="algo-stat-row">
        <div className={`algo-stat${coverage < 100 ? " algo-stat-accent" : ""}`}>
          <span className="algo-stat-label">Residents with a primary carer</span>
          <span className="algo-stat-value">
            {coverage}%
            <small>
              {" "}
              {data.residents_with_primary}/{data.total_residents}
            </small>
          </span>
        </div>
        <div className="algo-stat">
          <span className="algo-stat-label">No carer at all</span>
          <span className="algo-stat-value">{data.residents_with_no_carer}</span>
        </div>
        <div className="algo-stat">
          <span className="algo-stat-label">Active staff</span>
          <span className="algo-stat-value">{data.total_active_staff}</span>
        </div>
        <div className="algo-stat">
          <span className="algo-stat-label">Average caseload</span>
          <span className="algo-stat-value">{data.average_caseload}</span>
        </div>
      </div>

      <h2 className="section-title">Residents without a primary carer</h2>
      {data.unassigned.length ? (
        <Table
          columns={unassignedColumns}
          rows={data.unassigned}
          rowKey="resident_id"
          onRowClick={(row) => navigate(`/admin/residents/${row.resident_id}/care-team`)}
          emptyMessage="Every resident has a primary carer."
        />
      ) : (
        <EmptyState
          title="Every resident has a primary carer"
          message="Nothing needs attention here."
        />
      )}

      {applied && <ApplyResult result={applied} />}

      {/* Directly under the list of gaps, because that is the list it fills. */}
      {data.unassigned.length > 0 && (
        <AllocationPlan
          onApplied={(outcome) => {
            setApplied(outcome);
            setVersion((v) => v + 1);
          }}
        />
      )}

      <h2 className="section-title">Staff with no assigned residents</h2>
      {data.staff_without_caseload.length ? (
        <>
          <p className="text-muted">
            Not necessarily a problem &mdash; kitchen, laundry and administrative staff would
            not normally hold a caseload.
          </p>
          <Table
            columns={staffColumns}
            rows={data.staff_without_caseload}
            rowKey="employee_id"
            onRowClick={(row) => navigate(`/admin/employees/${row.employee_id}/caseload`)}
            emptyMessage="Everyone has a caseload."
          />
        </>
      ) : (
        <EmptyState title="Every active staff member has a caseload" />
      )}
    </div>
  );
}
