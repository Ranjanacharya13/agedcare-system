import { useState } from "react";
import { Link } from "react-router-dom";
import FormField from "../components/common/FormField.jsx";
import Button from "../components/common/Button.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import Logo from "../components/layout/Logo.jsx";
import { appointmentsConfig } from "../config/appointments.config.js";
import { post } from "../api/client.js";
import front1 from "../images/front1.jpg";
import front2 from "../images/front2.jpeg";

// Deliberately not built on ResourcePanel -- a visitor needs a one-shot
// intake form with a confirmation state, not a data table with edit/delete.
// Reuses the same field config as the admin Appointments page (minus the
// editOnly admin fields) so the two surfaces can't drift out of sync.
const publicFields = appointmentsConfig.fields.filter((field) => !field.editOnly);

function buildInitialValues() {
  return Object.fromEntries(publicFields.map((field) => [field.name, field.defaultValue ?? null]));
}

export default function PublicLandingPage() {
  const [values, setValues] = useState(buildInitialValues);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await post("/appointments", values);
      setSubmitted(true);
    } catch (err) {
      setError(err);
      setSubmitting(false);
    }
  };

  return (
    <div className="public-page">
      <div className="public-layout">
        <div className="public-images fade-slide-in">
          <img src={front1} alt="Caregiver checking in with a resident" />
          <img src={front2} alt="Caregiver walking with a resident in the garden" />
        </div>

        <div className="public-card fade-slide-in">
          <Logo tone="light" />
          <h1>Book a Visit</h1>
          <p className="text-muted">
            Tell us a little about what you're looking for and our team will reach out to
            schedule a facility tour or consultation.
          </p>

          {submitted ? (
            <div className="public-success fade-slide-in">
              <p className="empty-state-title">Thank you!</p>
              <p className="text-muted">
                We've received your request and will be in touch shortly to confirm a time.
              </p>
            </div>
          ) : (
            <form className="resource-form" onSubmit={handleSubmit}>
              <ErrorBanner error={error} />
              {publicFields.map((field) => (
                <FormField
                  key={field.name}
                  field={field}
                  value={values[field.name]}
                  onChange={(value) => handleChange(field.name, value)}
                />
              ))}
              <Button type="submit" variant="primary" disabled={submitting}>
                {submitting ? "Sending…" : "Request Appointment"}
              </Button>
            </form>
          )}
        </div>
      </div>

      <Link to="/admin" className="public-staff-link">
        Staff Portal →
      </Link>
    </div>
  );
}
