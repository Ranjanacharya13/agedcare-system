import { useMemo, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { suggestAssignments } from "../../api/algorithms.js";
import { createAssignmentsInBulk, bookNextFreeHour } from "../../api/assignments.js";
import { dayBounds } from "../../hooks/useStaffStatus.js";
import { isAborted } from "../../api/client.js";
import { localDateString } from "../../utils/format.js";
import Button from "../common/Button.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import StatusBadge from "../common/StatusBadge.jsx";

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
          start_date: localDateString(),
        })),
    [choices]
  );

  const confirm = async () => {
    setSaving(true);
    setError(null);
    try {
      const outcome = await createAssignmentsInBulk(confirmed);
      // book each new carer's next free hour too, so it shows up on today's dashboard
      const dayRange = dayBounds(new Date());
      await Promise.all(
        outcome.created.map((row) =>
          bookNextFreeHour(row.resident_id, row.employee_id, dayRange).catch(() => null)
        )
      );
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
        Ranks carers for each resident using Simple Additive Weighting (SAW) on workload and clinical fit,
        taking the highest-risk residents first and counting each pick towards that carer's load. Hard rules
        like caring role eligibility are prioritized lexicographically. Change anyone you disagree with,
        untick anyone you are not ready to decide, then confirm.
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
                carer is scored by Simple Additive Weighting (SAW on workload and clinical fit), and a caring
                role always ranks ahead of a non-clinical one via lexicographic priority.{" "}
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
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", flexWrap: "wrap" }}>
          <strong>{row.first_name} {row.last_name}</strong>
          {row.risk_band && <StatusBadge value={row.risk_band} badgeKind="riskBand" />}
        </div>
        <small className="algo-subtle">
          {row.room_number ? `Room ${row.room_number}` : "No room"}
          {row.risk_score !== null && row.risk_score !== undefined && ` · Risk score ${row.risk_score}`}
        </small>
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
            {/* text label, not just styling, so edited lines are obvious on review */}
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

/** Rendered by the page, not the panel, so the result survives even if confirming filled the last gap. */
export function ApplyResult({ result }) {
  const created = result.created.length;
  const tone = result.failed.length > 0 ? "plan-result has-failures" : "plan-result";

  return (
    <div className={tone} role="status">
      <p>
        <strong>
          {created} carer{created === 1 ? "" : "s"} assigned.
        </strong>{" "}
        {/* don't claim the job is done above a list of residents it isn't done for */}
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
