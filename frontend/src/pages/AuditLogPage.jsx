import { useCallback, useMemo, useState } from "react";
import { useAsync } from "../hooks/useAsync.js";
import { listAuditLog } from "../api/auth.js";
import Table from "../components/common/Table.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import StatusBadge from "../components/common/StatusBadge.jsx";
import Button from "../components/common/Button.jsx";
import { formatDateTime } from "../utils/format.js";
import { AUDIT_ACTION } from "../config/enums.js";

const PAGE_SIZE = 50;

/** Renders {field: {from, to}} as readable lines rather than raw JSON. */
function Changes({ changes }) {
  const entries = Object.entries(changes || {});
  if (!entries.length) return <span className="text-muted">—</span>;

  return (
    <ul className="audit-changes">
      {entries.map(([field, { from, to }]) => (
        <li key={field}>
          <code>{field}</code>{" "}
          <span className="audit-change-from">{format(from)}</span>
          {" → "}
          <span className="audit-change-to">{format(to)}</span>
        </li>
      ))}
    </ul>
  );
}

function format(value) {
  if (value === null || value === undefined) return "empty";
  if (typeof value === "object") return JSON.stringify(value);
  const text = String(value);
  return text.length > 60 ? `${text.slice(0, 60)}…` : text;
}

export default function AuditLogPage() {
  const [page, setPage] = useState(0);
  const [actionFilter, setActionFilter] = useState("");

  const load = useCallback(
    (signal) => listAuditLog({ skip: page * PAGE_SIZE, limit: PAGE_SIZE }, { signal }),
    [page]
  );
  const { data, loading, error } = useAsync(load, [load]);

  const rows = useMemo(() => {
    const entries = data || [];
    return actionFilter ? entries.filter((e) => e.action === actionFilter) : entries;
  }, [data, actionFilter]);

  const columns = [
    {
      key: "created_at",
      label: "When",
      render: (row) => formatDateTime(row.created_at),
    },
    {
      key: "actor_email",
      label: "Who",
      render: (row) => (
        <span>
          {row.actor_email || <span className="text-muted">anonymous</span>}
          {row.actor_role && <small className="audit-actor-role">{row.actor_role}</small>}
        </span>
      ),
    },
    {
      key: "action",
      label: "Action",
      render: (row) => <StatusBadge value={row.action} badgeKind="auditAction" />,
    },
    {
      key: "table_name",
      label: "Record",
      render: (row) => (
        <span>
          {row.table_name}
          {row.record_id && <small className="audit-record-id">{row.record_id.slice(0, 8)}</small>}
        </span>
      ),
    },
    {
      key: "changes",
      label: "What changed",
      render: (row) => (row.detail ? row.detail : <Changes changes={row.changes} />),
    },
  ];

  return (
    <div className="page">
      <h1 className="page-title">Audit Log</h1>
      <p className="text-muted page-intro">
        Every change to a record, plus sign-ins and refused requests. The log is append-only —
        entries cannot be edited or removed, including by an administrator.
      </p>

      <div className="audit-toolbar">
        <label className="form-field-label" htmlFor="audit-action-filter">
          Action
        </label>
        <select
          id="audit-action-filter"
          className="input-text"
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
        >
          <option value="">All actions</option>
          {AUDIT_ACTION.map((action) => (
            <option key={action} value={action}>
              {action.replace(/_/g, " ")}
            </option>
          ))}
        </select>
      </div>

      <ErrorBanner error={error} />

      {loading ? (
        <Skeleton rows={6} />
      ) : (
        <>
          <Table
            columns={columns}
            rows={rows}
            emptyMessage={
              actionFilter
                ? `No ${actionFilter.replace(/_/g, " ")} entries on this page.`
                : "Nothing recorded yet."
            }
          />
          <div className="pager">
            <Button
              variant="secondary"
              size="sm"
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
            >
              Previous
            </Button>
            <span className="text-muted">Page {page + 1}</span>
            <Button
              variant="secondary"
              size="sm"
              disabled={(data || []).length < PAGE_SIZE}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
