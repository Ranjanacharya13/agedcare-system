import { useCallback, useState } from "react";
import { useAsync } from "../../hooks/useAsync.js";
import { useAuth } from "../../context/AuthContext.jsx";
import { getSuggestedCarers } from "../../api/algorithms.js";
import { bookNextFreeHour, createAssignment } from "../../api/assignments.js";
import { dayBounds, shiftLabel } from "../../hooks/useStaffStatus.js";
import { isAborted } from "../../api/client.js";
import { localDateString } from "../../utils/format.js";
import { createResourceApi } from "../../api/resourceApi.js";
import { shifts as shiftsConfig } from "../../config/employeeResourceConfigs.js";
import Button from "../common/Button.jsx";
import Modal from "../common/Modal.jsx";
import ResourceForm from "../resource/ResourceForm.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

const SHOWN = 3;
const shiftsApi = createResourceApi(shiftsConfig);

export default function SuggestedCarers({
  residentId,
  version = 0,
  hasPrimary = false,
  onAssigned,
}) {
  const { can } = useAuth();
  const [assigning, setAssigning] = useState(null);
  const [error, setError] = useState(null);
  const [booked, setBooked] = useState(null);
  const [shiftFor, setShiftFor] = useState(null); // {employeeId, name} while the create-shift modal is open

  const load = useCallback(
    (signal) => getSuggestedCarers(residentId, dayBounds(new Date()), { signal }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [residentId, version]
  );
  const { data, loading, error: loadError } = useAsync(load, [load]);

  const assignmentType = hasPrimary ? "Secondary" : "Primary";

  const assign = async (candidate) => {
    setAssigning(candidate.employee_id);
    setError(null);
    setBooked(null);
    const name = candidate.first_name;
    try {
      await createAssignment(residentId, {
        employee_id: candidate.employee_id,
        assignment_type: assignmentType,
        start_date: localDateString(),
      });
      // Match them for today too: their next free hour on shift, so it shows on the dashboard.
      let visit = null;
      if (candidate.on_shift_today) {
        try {
          visit = await bookNextFreeHour(residentId, candidate.employee_id, dayBounds(new Date()));
        } catch (err) {
          setError(err); // the assignment stands; only today's slot failed
        }
      }
      setBooked(
        visit
          ? { tone: "success", text: `${name} assigned and with this resident today ${shiftLabel({ shift_start: visit.start_at, shift_end: visit.end_at })}.` }
          : {
              tone: "warning",
              text: candidate.on_shift_today
                ? `${name} assigned, but has no free hour left on today's shift.`
                : `${name} assigned, but is not rostered today, so nothing was booked for today.`,
              employeeId: candidate.employee_id,
              name,
            }
      );
      onAssigned?.();
    } catch (err) {
      if (!isAborted(err)) setError(err);
    } finally {
      setAssigning(null);
    }
  };

  const handleShiftCreated = async (values) => {
    await shiftsApi.create(values, { parentId: shiftFor.employeeId });
    setShiftFor(null);
    // Now that they have a shift today, try booking the visit that failed before.
    try {
      const visit = await bookNextFreeHour(residentId, shiftFor.employeeId, dayBounds(new Date()));
      setBooked(
        visit
          ? {
              tone: "success",
              text: `${shiftFor.name} is now with this resident today ${shiftLabel({ shift_start: visit.start_at, shift_end: visit.end_at })}.`,
            }
          : { tone: "warning", text: `Shift created, but no free hour was left in it for this resident.`, employeeId: shiftFor.employeeId, name: shiftFor.name }
      );
    } catch (err) {
      if (!isAborted(err)) setError(err);
    }
  };

  if (!can("assignments", "write")) return null;
  if (loading) return <Skeleton rows={2} />;
  const bookedNote = booked && (
    <p className={`suggestion-booked tone-${booked.tone}`} role="status">
      {booked.text}
      {booked.tone === "warning" && booked.employeeId && (
        <Button
          size="sm"
          variant="secondary"
          onClick={() => setShiftFor({ employeeId: booked.employeeId, name: booked.name })}
        >
          Create a shift for them
        </Button>
      )}
    </p>
  );
  const shiftModal = shiftFor && (
    <Modal title={`Add a shift for ${shiftFor.name}`} onClose={() => setShiftFor(null)}>
      <ResourceForm
        resource={shiftsConfig}
        record={null}
        parentId={shiftFor.employeeId}
        onSubmit={handleShiftCreated}
        onCancel={() => setShiftFor(null)}
      />
    </Modal>
  );

  if (loadError || !data?.length) {
    return (
      <>
        {bookedNote}
        {shiftModal}
      </>
    );
  }

  return (
    <div className="suggestion-box">
      <div className="suggestion-header-row">
        <p className="suggestion-heading">
          Suggested {assignmentType.toLowerCase()} carer
          {hasPrimary && <span className="text-muted"> &mdash; this resident already has a key worker</span>}
        </p>
      </div>

      <ErrorBanner error={error} />
      {bookedNote}

      <ul className="suggestion-list">
        {data.slice(0, SHOWN).map((candidate, index) => {
          const suitabilityPct = Math.round(candidate.saw_score * 100);

          return (
            <li key={candidate.employee_id} className="suggestion-item">
              <div className="suggestion-person">
                <div className="suggestion-person-header">
                  <span className="suggestion-rank-badge">#{candidate.rank || index + 1}</span>
                  <strong>
                    {candidate.first_name} {candidate.last_name}
                  </strong>
                  {candidate.role && <span className="text-muted"> · {candidate.role}</span>}
                  <span className="saw-score-pill">{suitabilityPct}% match</span>
                </div>
                <span className={`picker-shift ${candidate.on_shift_today ? "on" : "off"}`}>
                  {candidate.on_shift_today
                    ? `On shift today ${shiftLabel({ shift_start: candidate.shift_start, shift_end: candidate.shift_end })}`
                    : "Not rostered today"}
                </span>
                <small className="suggestion-reason">{candidate.reason}</small>

                {candidate.breakdown && candidate.breakdown.length > 0 && (
                  <details className="suggestion-breakdown-details">
                    <summary>Why this score? (SAW)</summary>
                    <div className="suggestion-breakdown-grid">
                      {candidate.breakdown.map((b) => (
                        <div key={b.criterion} className="suggestion-breakdown-item">
                          <span className="text-muted">{b.criterion.replace(/_/g, " ")}:</span>
                          <strong>+{Math.round(b.contribution * 100)}%</strong>
                          <span className="algo-subtle">(w={b.weight})</span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>

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
          );
        })}
      </ul>

      <p className="suggestion-footnote">
        Staff on shift today come first, then Simple Additive Weighting (SAW) on caseload and
        clinical acuity. Only care roles are listed. Assigning also books their next free hour today.
        Advisory only &mdash; assign whoever actually knows them, using
        the form below if they are not listed here.
      </p>
      {shiftModal}
    </div>
  );
}
