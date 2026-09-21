import { useCallback, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAsync } from "../../hooks/useAsync.js";
import { useAuth } from "../../context/AuthContext.jsx";
import {
  getCareTeam,
  createAssignment,
  reassignCarer,
  endAssignment,
  changeAssignmentType,
} from "../../api/assignments.js";
import { isAborted } from "../../api/client.js";
import SuggestedCarers from "./SuggestedCarers.jsx";
import CarerPicker from "./CarerPicker.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import Button from "../common/Button.jsx";
import Modal from "../common/Modal.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import { formatDateTime, initials } from "../../utils/format.js";

export default function CareTeamPanel({ residentId }) {
  const { can } = useAuth();
  const canEdit = can("assignments", "write");

  const [version, setVersion] = useState(0);
  const [picker, setPicker] = useState(null); // {mode:"add"} | {mode:"reassign", member}
  const [ending, setEnding] = useState(null);
  const [actionError, setActionError] = useState(null);

  const load = useCallback(
    (signal) => getCareTeam(residentId, { signal }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [residentId, version]
  );
  const { data, loading, error } = useAsync(load, [load]);

  const refresh = () => setVersion((v) => v + 1);

  const activeMembers = useMemo(() => (data?.members || []).filter((m) => m.active), [data]);
  const pastMembers = useMemo(() => (data?.members || []).filter((m) => !m.active), [data]);
  const takenIds = useMemo(
    () => new Set(activeMembers.map((m) => m.employee_id)),
    [activeMembers]
  );

  const run = async (fn) => {
    setActionError(null);
    try {
      await fn();
      refresh();
    } catch (err) {
      if (!isAborted(err)) setActionError(err);
    }
  };

  const handlePick = async (employeeId, type) => {
    if (picker.mode === "reassign") {
      await reassignCarer(residentId, picker.member.assignment_id, { employee_id: employeeId });
    } else {
      await createAssignment(residentId, {
        employee_id: employeeId,
        assignment_type: type,
        start_date: new Date().toISOString().slice(0, 10),
      });
    }
    setPicker(null);
    refresh();
  };

  return (
    <div className="care-team">
      {loading && !data && <Skeleton rows={3} />}
      <ErrorBanner error={error || actionError} />

      {data && (
        <>
          {!data.has_primary && (
            <p className="coverage-warning" role="status">
              No primary carer assigned. Every resident should have one named key worker who
              knows them and is the family&rsquo;s point of contact.
            </p>
          )}

          <div className="care-team-toolbar">
            <p className="text-muted care-team-summary">
              {activeMembers.length} active carer{activeMembers.length === 1 ? "" : "s"}
              {data.on_shift_count > 0
                ? ` · ${data.on_shift_count} on shift right now`
                : activeMembers.length > 0
                  ? " · none currently on shift"
                  : ""}
            </p>
            {canEdit && (
              <Button size="sm" onClick={() => setPicker({ mode: "add" })}>
                + Add a carer
              </Button>
            )}
          </div>

          {activeMembers.length === 0 && (
            <p className="text-muted">Nobody is assigned to this resident yet.</p>
          )}

          <ul className="care-team-list">
            {activeMembers.map((member) => (
              <li key={member.assignment_id} className="care-team-member">
                <span className="care-team-avatar" aria-hidden="true">
                  {initials(member.first_name, member.last_name)}
                </span>
                <span className="care-team-identity">
                  <Link to={`/admin/employees/${member.employee_id}`}>
                    {member.first_name} {member.last_name}
                  </Link>
                  <small>{member.role || "Role not set"}</small>
                </span>
                <StatusBadge value={member.assignment_type} badgeKind="assignmentType" />
                <span className="care-team-shift">
                  {member.on_shift_now ? (
                    <span className="on-shift-now">On shift now</span>
                  ) : member.next_shift_start ? (
                    <span className="text-muted">Next: {formatDateTime(member.next_shift_start)}</span>
                  ) : (
                    <span className="text-muted">No upcoming shift</span>
                  )}
                </span>
                {canEdit && (
                  <span className="care-team-actions">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setPicker({ mode: "reassign", member })}
                    >
                      Reassign
                    </Button>
                    {member.assignment_type !== "Primary" && !data.has_primary && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() =>
                          run(() =>
                            changeAssignmentType(residentId, member.assignment_id, "Primary")
                          )
                        }
                      >
                        Make primary
                      </Button>
                    )}
                    <Button size="sm" variant="secondary" onClick={() => setEnding(member)}>
                      End
                    </Button>
                  </span>
                )}
              </li>
            ))}
          </ul>

          {canEdit && (
            <SuggestedCarers
              residentId={residentId}
              version={version}
              hasPrimary={data.has_primary}
              onAssigned={refresh}
            />
          )}

          {pastMembers.length > 0 && (
            <details className="care-team-history">
              <summary>Previous carers ({pastMembers.length})</summary>
              <ul className="care-team-list">
                {pastMembers.map((member) => (
                  <li key={member.assignment_id} className="care-team-member is-ended">
                    <span className="care-team-avatar" aria-hidden="true">
                      {initials(member.first_name, member.last_name)}
                    </span>
                    <span className="care-team-identity">
                      <Link to={`/admin/employees/${member.employee_id}`}>
                        {member.first_name} {member.last_name}
                      </Link>
                      <small>{member.role || "Role not set"}</small>
                    </span>
                    <StatusBadge value={member.assignment_type} badgeKind="assignmentType" />
                    <span className="text-muted">
                      {member.start_date || "?"} → {member.end_date || "?"}
                    </span>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}

      {picker && (
        <CarerPicker
          mode={picker.mode}
          currentMember={picker.member}
          takenEmployeeIds={takenIds}
          hasPrimary={data?.has_primary}
          onConfirm={handlePick}
          onClose={() => setPicker(null)}
        />
      )}

      {ending && (
        <Modal
          title="End this assignment?"
          onClose={() => setEnding(null)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setEnding(null)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={async () => {
                  const member = ending;
                  setEnding(null);
                  await run(() => endAssignment(residentId, member.assignment_id));
                }}
              >
                End assignment
              </Button>
            </>
          }
        >
          <p>
            {ending.first_name} {ending.last_name} will no longer be {ending.assignment_type.toLowerCase()}{" "}
            carer for this resident from today. The record is kept as history.
          </p>
        </Modal>
      )}
    </div>
  );
}
