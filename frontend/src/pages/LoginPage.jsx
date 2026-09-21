import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Logo from "../components/layout/Logo.jsx";
import { IconKangaroo } from "../components/layout/Icons.jsx";
import Button from "../components/common/Button.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const from = location.state?.from?.pathname || "/admin";

  useEffect(() => {
    if (isAuthenticated) navigate(from, { replace: true });
  }, [isAuthenticated, from, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      // The effect above redirects once the context updates.
    } catch (err) {
      setError({ message: err.message || "Could not sign you in." });
      setSubmitting(false);
    }
  };

  return (
    <div className="public-page">
      <div className="login-card fade-slide-in">
        <IconKangaroo size={150} className="public-card-mascot" />
        <Logo tone="light" />
        <h1>Staff Sign In</h1>
        <p className="text-muted">Sign in to access the CareOS admin console.</p>

        <form className="resource-form" onSubmit={handleSubmit}>
          <ErrorBanner error={error} />
          <div className="form-field">
            <label className="form-field-label" htmlFor="login-email">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              className="input-text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoFocus
              autoComplete="username"
              required
            />
          </div>
          <div className="form-field">
            <label className="form-field-label" htmlFor="login-password">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              className="input-text"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          <Button type="submit" variant="primary" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign In"}
          </Button>
        </form>

        <p className="login-hint">
          No account? Ask an administrator to create one for you — accounts are
          issued, not self-registered.
        </p>

        <Link to="/" className="login-back-link">
          ← Back to public site
        </Link>
      </div>
    </div>
  );
}
