import { useState } from "react";
import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import Modal from "../components/common/Modal.jsx";
import Button from "../components/common/Button.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import { usersConfig } from "../config/users.config.js";
import { resetUserPassword } from "../api/auth.js";
import { useAuth } from "../context/AuthContext.jsx";
import { ACCESS_ROLES, can } from "../config/permissions.js";

const ROLES = Object.values(ACCESS_ROLES).filter((r) => r !== ACCESS_ROLES.FAMILY);
const CAPABILITIES = [
  ["View residents and care teams", "residents", "read"],
  ["Daily charts and incidents", "resident_charts", "write"],
  ["Edit residents, medications, assessments", "resident_clinical", "write"],
  ["Assign carers to residents", "assignments", "write"],
  ["View staff and rosters", "employees", "read"],
  ["Edit staff and rosters", "employees", "write"],
  ["HR: contracts, pay, leave", "employee_hr", "read"],
  ["Complaints", "complaints", "read"],
  ["Manage appointments", "appointments", "write"],
  ["Audit log", "audit", "read"],
  ["Login accounts", "users", "write"],
];

function RoleMatrix() {
  return (
    <details className="card role-matrix">
      <summary>What can each role do?</summary>
      <table className="data-table">
        <thead>
          <tr>
            <th>Capability</th>
            {ROLES.map((r) => (
              <th key={r}>{r}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {CAPABILITIES.map(([label, group, action]) => (
            <tr key={label}>
              <td>{label}</td>
              {ROLES.map((r) => (
                <td key={r}>{can(r, group, action) ? "✓" : "—"}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  );
}

const MIN_PASSWORD_LENGTH = 12;

function ResetPasswordModal({ account, onClose }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [done, setDone] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await resetUserPassword(account.id, password);
      setDone(true);
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal title={`Reset password — ${account.email}`} onClose={onClose}>
      {done ? (
        <div>
          <p>
            Password reset. Give it to {account.full_name || account.email} directly, and ask them
            to change it after signing in.
          </p>
          <div className="resource-form-actions">
            <Button variant="primary" onClick={onClose}>
              Done
            </Button>
          </div>
        </div>
      ) : (
        <form className="resource-form" onSubmit={submit}>
          <ErrorBanner error={error} />
          <p className="text-muted">
            You are setting a new password for this account. The existing one is never shown —
            it is stored only as a hash, so nobody, including you, can read it back.
          </p>
          <div className="form-field">
            <label className="form-field-label" htmlFor="reset-password">
              New password<span className="required-mark">*</span>
            </label>
            <input
              id="reset-password"
              type="password"
              className="input-text"
              minLength={MIN_PASSWORD_LENGTH}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              required
            />
          </div>
          <div className="resource-form-actions">
            <Button type="button" variant="secondary" onClick={onClose} disabled={saving}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={saving}>
              {saving ? "Resetting…" : "Reset password"}
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
}

export default function UsersPage() {
  const { user } = useAuth();
  const [resetTarget, setResetTarget] = useState(null);

  return (
    <div className="page">
      <h1 className="page-title">Login Accounts</h1>
      <p className="text-muted page-intro">
        Accounts are issued here &mdash; there is no self-registration. An account is a way to
        sign in; the <strong>access role</strong> decides what that person may see. This is
        deliberately separate from <strong>Staff (HR)</strong>: job title lives on the
        employment record, and the two are not the same thing (a Care Coordinator might hold
        Manager access, and a family member will one day have an account with no employment
        record at all).
      </p>

      <RoleMatrix />

      <ResourcePanel
        resource={usersConfig}
        extraRowActions={(row) => (
          <>
            <Button variant="secondary" size="sm" onClick={() => setResetTarget(row)}>
              Reset password
            </Button>
            {row.id === user?.id && <span className="row-note">you</span>}
          </>
        )}
      />

      {resetTarget && (
        <ResetPasswordModal account={resetTarget} onClose={() => setResetTarget(null)} />
      )}
    </div>
  );
}
