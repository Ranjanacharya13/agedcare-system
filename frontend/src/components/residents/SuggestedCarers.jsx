import { useCallback, useState } from "react";
import { useAsync } from "../../hooks/useAsync.js";
import { useAuth } from "../../context/AuthContext.jsx";
import { getSuggestedCarers } from "../../api/algorithms.js";
import { createAssignment } from "../../api/assignments.js";
import { isAborted } from "../../api/client.js";
import Button from "../common/Button.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

const SHOWN = 3;

export default function SuggestedCarers({
  residentId,
  version = 0,
  hasPrimary = false,
  onAssigned,
}) {
  const { can } = useAuth();
  const [assigning, setAssigning] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(
    (signal) => getSuggestedCarers(residentId, { signal }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [residentId, version]
  );
  const { data, loading, error: loadError } = useAsync(load, [load]);

  const assignmentType = hasPrimary ? "Secondary" : "Primary";

  const assign = async (candidate) => {
    setAssigning(candidate.employee_id);
    setError(null);
    try {
      await createAssignment(residentId, {
        employee_id: candidate.employee_id,
        assignment_type: assignmentType,
        start_date: new Date().toISOString().slice(0, 10),
      });
      onAssigned?.();
    } catch (err) {
      if (!isAborted(err)) setError(err);
    } finally {
      setAssigning(null);
    }
  };

  if (!can("assignments", "write")) return null;
  if (loading) return <Skeleton rows={2} />;
  if (loadError || !data?.length) return null;

  return (
    <div className="suggestion-box">
      <p className="suggestion-heading">
        Suggested {assignmentType.toLowerCase()} carer
        {hasPrimary && <span className="text-muted"> &mdash; this resident already has a key worker</span>}
      </p>

      <ErrorBanner error={error} />

      <ul className="suggestion-list">
        {data.slice(0, SHOWN).map((candidate, index) => (
          <li key={candidate.employee_id}>
            <span className="suggestion-person">
              <strong>
                {candidate.first_name} {candidate.last_name}
              </strong>
              {candidate.role && <span className="text-muted"> · {candidate.role}</span>}
              <small className="suggestion-reason">{candidate.reason}</small>
            </span>
            <Button
              size="sm"
              variant={index === 0 ? "primary" : "secondary"}
              onClick={() => assign(candidate)}
              disabled={Boolean(assigning)}
            >
              {assigning === candidate.employee_id
                ? "Assigning…"
                : `Assign as ${assignmentType.toLowerCase()}`}
            </Button>
          </li>
        ))}
      </ul>

      <p className="suggestion-footnote">
        Ranked by how much each staff member is already carrying and how well their role fits this
        resident&rsquo;s needs. Advisory only &mdash; assign whoever actually knows them, using the
        form below if they are not listed here.
      </p>
    </div>
  );
}
