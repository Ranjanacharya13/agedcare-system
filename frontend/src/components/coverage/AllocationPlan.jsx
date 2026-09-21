import { useMemo, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { suggestAssignments } from "../../api/algorithms.js";
import { createAssignmentsInBulk } from "../../api/assignments.js";
import { isAborted } from "../../api/client.js";
import Button from "../common/Button.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

export default function AllocationPlan({ onApplied }) {
  const { can } = useAuth();
  const [plan, setPlan] = useState(null);
  const [choices, setChoices] = useState({});
  const [running, setRunning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    setRunning(true);
    setError(null);
    try {
      const next = await suggestAssignments();
      setPlan(next);
      setChoices(
        Object.fromEntries(
          next.suggestions.map((row) => [
            row.resident_id,
            { employeeId: row.employee_id || "", include: Boolean(row.employee_id) },
          ])
        )
      );
    } catch (err) {
      if (!isAborted(err)) setError(err);
    } finally {
      setRunning(false);
    }
  };

  const setChoice = (residentId, patch) =>
    setChoices((current) => ({
      ...current,
      [residentId]: { ...current[residentId], ...patch },
    }));

  const confirmed = useMemo(
    () =>
      Object.entries(choices)
        .filter(([, choice]) => choice.include && choice.employeeId)
        .map(([resident_id, choice]) => ({
          resident_id,
          employee_id: choice.employeeId,
          assignment_type: "Primary",
        })),
    [choices]
  );

  const confirm = async () => {
    setSaving(true);
    setError(null);
    try {
      const outcome = await createAssignmentsInBulk(confirmed);
      setPlan(null);
      setChoices({});
      onApplied?.(outcome);
    } catch (err) {
      if (!isAborted(err)) setError(err);
    } finally {
      setSaving(false);
    }
  };

  if (!can("assignments", "write")) return null;

  return (
    <section className="algo-panel">
      <h2 className="section-title">Suggest a carer for each</h2>
      <p className="text-muted">
        Ranks carers for each resident by workload and clinical fit, taking the highest-risk
        residents first and counting each pick towards that carer's load. Change anyone you
        disagree with, untick anyone you are not ready to decide, then confirm.
      </p>

      <Button variant="secondary" onClick={run} disabled={running || saving}>
        {running ? "Working it out…" : plan ? "Start again" : "Suggest carers"}
      </Button>

      <ErrorBanner error={error} />
      {running && <Skeleton rows={4} />}

      {plan && !running && (
        <>
          {plan.suggestions.length === 0 ? (
            <p className="algo-note">
              Nothing to allocate &mdash; every active resident already has a primary carer.
            </p>
          ) : (
            <>
              <div className="table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th className="plan-include-cell">Assign</th>
                      <th>Resident</th>
                      <th>Primary carer</th>
                      <th>Why</th>
                    </tr>
                  </thead>
                  <tbody>
                    {plan.suggestions.map((row) => (
                      <PlanRow
                        key={row.resident_id}
                        row={row}
                        choice={choices[row.resident_id]}
                        onChange={(patch) => setChoice(row.resident_id, patch)}
                      />
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="plan-actions">
                <Button onClick={confirm} disabled={saving || confirmed.length === 0}>
                  {saving
                    ? "Assigning…"
                    : `Confirm ${confirmed.length} assignment${confirmed.length === 1 ? "" : "s"}`}
                </Button>
                <span className="text-muted">
                  Creates each as the resident&rsquo;s <strong>primary</strong> carer, starting
                  today. Nothing is written until you confirm.
                </span>
              </div>

              <p className="algo-meta">
                {plan.residents_needing_a_carer} resident(s) ranked against{" "}
                {plan.candidates_considered} staff member(s), highest-risk resident first. Each
                carer is scored by weighted criteria (workload and clinical fit), and a caring
                role always ranks ahead of a non-clinical one.{" "}
                {plan.unmatched > 0 && (
                  <strong>
                    {plan.unmatched} resident(s) could not be matched at all &mdash; there are
                    not enough eligible staff.
                  </strong>
                )}
              </p>
            </>
          )}
        </>
      )}
    </section>
  );
}

/** One editable line of the plan. */
function PlanRow({ row, choice, onChange }) {
  const options = row.alternatives || [];
  const selected = options.find((c) => c.employee_id === choice?.employeeId);
  const changed = Boolean(row.employee_id) && choice?.employeeId !== row.employee_id;

  return (
    <tr className={choice?.include ? "" : "plan-row-skipped"}>
      <td className="plan-include-cell">
        <input
          type="checkbox"
          checked={Boolean(choice?.include)}
          disabled={options.length === 0}
          onChange={(event) => onChange({ include: event.target.checked })}
          aria-label={`Assign a carer to ${row.first_name} ${row.last_name}`}
        />
      </td>
      <td>
        {row.first_name} {row.last_name}
        {row.room_number && <small className="algo-subtle">Room {row.room_number}</small>}
      </td>
      <td>
        {options.length === 0 ? (
          <span className="coverage-critical">Nobody available</span>
        ) : (
          <>
            <select
              className="plan-carer-select"
              value={choice?.employeeId || ""}
              onChange={(event) => onChange({ employeeId: event.target.value })}
              aria-label={`Primary carer for ${row.first_name} ${row.last_name}`}
            >
              {options.map((candidate) => (
                <option key={candidate.employee_id} value={candidate.employee_id}>
                  {candidate.first_name} {candidate.last_name}
                  {candidate.role ? ` · ${candidate.role}` : ""}
                </option>
              ))}
            </select>
            {/* Named rather than merely styled, so it is obvious on review
                which lines are the user's own decisions. */}
            {changed && <small className="algo-subtle">changed from suggestion</small>}
          </>
        )}
      </td>
      <td>
        <span className="suggestion-reason">{selected?.reason || row.reason}</span>
      </td>
    </tr>
  );
}

/** What actually happened when the plan was confirmed. Rendered by the page
 *  rather than the panel, so it outlives the gaps it just filled. */
export function ApplyResult({ result }) {
  const created = result.created.length;
  const tone = result.failed.length > 0 ? "plan-result has-failures" : "plan-result";

  return (
    <div className={tone} role="status">
      <p>
        <strong>
          {created} carer{created === 1 ? "" : "s"} assigned.
        </strong>{" "}
        {/* Only claim the whole job is done when it is. Saying "each
            resident now has a key worker" above a list of ones who do not
            is how a screen teaches people to stop reading it. */}
        {created > 0 &&
          result.failed.length === 0 &&
          "Each resident now has a named key worker on their care team."}
      </p>

      {result.failed.length > 0 && (
        <>
          <p className="coverage-critical">
            {result.failed.length} could not be assigned:
          </p>
          <ul className="plan-failures">
            {result.failed.map((failure) => (
              <li key={`${failure.resident_id}-${failure.employee_id}`}>{failure.reason}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
