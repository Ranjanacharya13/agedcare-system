import Modal from "../common/Modal.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import EmptyState from "../common/EmptyState.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import { useAsync } from "../../hooks/useAsync.js";
import { getSuggestedEmployees } from "../../api/shiftSuggestions.js";

export default function ShiftSuggestionsModal({ shiftId, onClose }) {
  const { data, loading, error } = useAsync(() => getSuggestedEmployees(shiftId), [shiftId]);

  return (
    <Modal title="Suggested Coverage" onClose={onClose}>
      <ErrorBanner error={error} />
      {loading ? (
        <Skeleton rows={3} />
      ) : !data?.length ? (
        <EmptyState message="No eligible employees found for this shift." />
      ) : (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Role</th>
                <th>Week Hours</th>
                <th>Care Load</th>
                <th>Conflict</th>
              </tr>
            </thead>
            <tbody>
              {data.map((s) => (
                <tr key={s.employee_id}>
                  <td>
                    {s.first_name} {s.last_name}
                  </td>
                  <td>{s.role || "—"}</td>
                  <td>{s.current_week_hours}</td>
                  <td>
                    {s.care_load_score}
                    {s.residents_cared_for_recently > 0 && (
                      <span className="text-muted">
                        {" "}
                        ({s.residents_cared_for_recently}{" "}
                        resident{s.residents_cared_for_recently === 1 ? "" : "s"})
                      </span>
                    )}
                  </td>
                  <td>
                    <StatusBadge
                      value={s.conflict ? "Conflict" : "Available"}
                      badgeKind="conflict"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Modal>
  );
}
