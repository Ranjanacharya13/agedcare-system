import { useState } from "react";
import Button from "../components/common/Button.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import { changePassword } from "../api/auth.js";
import { useAuth } from "../context/AuthContext.jsx";
import { formatDateTime } from "../utils/format.js";

const MIN_PASSWORD_LENGTH = 12;

export default function AccountPage() {
  const { user, role } = useAuth();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaved(false);

    if (next !== confirm) {
      setError({ message: "The two new passwords don't match." });
      return;
    }

    setSaving(true);
    try {
      await changePassword(current, next);
      setSaved(true);
      setCurrent("");
      setNext("");
      setConfirm("");
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page">
      <h1 className="page-title">Your Account</h1>

      <dl className="account-summary">
        <dt>Email</dt>
        <dd>{user?.email}</dd>
        <dt>Name</dt>
        <dd>{user?.full_name || "—"}</dd>
        <dt>Access role</dt>
        <dd>{role}</dd>
        <dt>Last sign-in</dt>
        <dd>{user?.last_login_at ? formatDateTime(user.last_login_at) : "This is your first"}</dd>
      </dl>

      <h2 className="section-title">Change password</h2>
      <form className="resource-form account-form" onSubmit={submit}>
        <ErrorBanner error={error} />
        {saved && (
          <div className="success-banner" role="status">
            Password changed. Your current sign-in stays valid.
          </div>
        )}

        <div className="form-field">
          <label className="form-field-label" htmlFor="current-password">
            Current password<span className="required-mark">*</span>
          </label>
          <input
            id="current-password"
            type="password"
            className="input-text"
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        <div className="form-field">
          <label className="form-field-label" htmlFor="new-password">
            New password<span className="required-mark">*</span>
          </label>
          <input
            id="new-password"
            type="password"
            className="input-text"
            minLength={MIN_PASSWORD_LENGTH}
            value={next}
            onChange={(e) => setNext(e.target.value)}
            autoComplete="new-password"
            required
          />
          <p className="text-muted">
            At least {MIN_PASSWORD_LENGTH} characters. Length matters far more than symbols — a
            short phrase of a few unrelated words is both stronger and easier to remember.
          </p>
        </div>

        <div className="form-field">
          <label className="form-field-label" htmlFor="confirm-password">
            Confirm new password<span className="required-mark">*</span>
          </label>
          <input
            id="confirm-password"
            type="password"
            className="input-text"
            minLength={MIN_PASSWORD_LENGTH}
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoComplete="new-password"
            required
          />
        </div>

        <div className="resource-form-actions">
          <Button type="submit" variant="primary" disabled={saving}>
            {saving ? "Saving…" : "Change password"}
          </Button>
        </div>
      </form>
    </div>
  );
}
