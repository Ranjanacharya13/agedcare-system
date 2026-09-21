import { useEffect, useRef, useState } from "react";
import { post, ApiError } from "../../api/client.js";
import { APPOINTMENT_SERVICE_OPTIONS } from "../../config/landingContent.js";
import { IconCheck, IconPhone } from "../layout/Icons.jsx";

const INITIAL_VALUES = {
  full_name: "",
  phone: "",
  email: "",
  appointment_type: "",
  preferred_date: "",
  preferred_time: "",
  message: "",
  consent: false,
  // Honeypot — must stay empty. See the hidden field in the form below.
  website: "",
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(values) {
  const errors = {};
  if (!values.full_name.trim()) {
    errors.full_name = "Enter your full name.";
  }
  if (!values.phone.trim()) {
    errors.phone = "Enter a phone number so we can reach you.";
  }
  if (!values.email.trim()) {
    errors.email = "Enter your email address.";
  } else if (!EMAIL_PATTERN.test(values.email.trim())) {
    errors.email = "Enter a valid email address, like name@example.com.";
  }
  if (!values.appointment_type) {
    errors.appointment_type = "Select the service you're enquiring about.";
  }
  if (!values.consent) {
    errors.consent = "Please confirm you're okay for us to contact you about this enquiry.";
  }
  return errors;
}

function Field({ id, label, required, error, hint, children }) {
  const errorId = `${id}-error`;
  const hintId = hint ? `${id}-hint` : undefined;
  return (
    <div className={`landing-field${error ? " has-error" : ""}`}>
      <label className="landing-field-label" htmlFor={id}>
        {label}
        {required && (
          <span className="landing-required" aria-hidden="true">
            {" "}
            *
          </span>
        )}
      </label>
      {hint && (
        <span className="landing-field-hint" id={hintId}>
          {hint}
        </span>
      )}
      {children({
        id,
        "aria-invalid": error ? "true" : undefined,
        "aria-describedby": [error ? errorId : null, hintId].filter(Boolean).join(" ") || undefined,
      })}
      {error && (
        <span className="landing-field-error" id={errorId} role="alert">
          {error}
        </span>
      )}
    </div>
  );
}

export default function AppointmentSection() {
  const [values, setValues] = useState(INITIAL_VALUES);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const errorSummaryRef = useRef(null);
  const successHeadingRef = useRef(null);

  useEffect(() => {
    if (Object.keys(errors).length > 0 && errorSummaryRef.current) {
      errorSummaryRef.current.focus();
    }
  }, [errors]);

  useEffect(() => {
    if (submitted && successHeadingRef.current) {
      successHeadingRef.current.focus();
    }
  }, [submitted]);

  const setField = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const validationErrors = validate(values);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setSubmitting(true);
    setSubmitError(null);
    try {
      await post("/appointments/public", {
        full_name: values.full_name.trim(),
        email: values.email.trim(),
        phone: values.phone.trim(),
        appointment_type: values.appointment_type,
        preferred_date: values.preferred_date || null,
        preferred_time: values.preferred_time || null,
        message: values.message.trim() || null,
        website: values.website,
      });
      setSubmitted(true);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message || "We couldn't submit your request. Please try again."
          : "We couldn't reach our server. Check your connection and try again.";
      setSubmitError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleBookAnother = () => {
    setValues(INITIAL_VALUES);
    setErrors({});
    setSubmitError(null);
    setSubmitted(false);
  };

  const errorList = Object.entries(errors);

  return (
    <section id="appointment" className="landing-section landing-section-alt">
      <div className="landing-container landing-appointment-inner">
        <div>
          <span className="landing-eyebrow">Book an appointment</span>
          <h2 className="landing-section-title">Let's talk about your family's needs</h2>
          <p className="landing-section-lead">
            Fill in the form and a member of our team will call you back within one business
            day. There's no cost or obligation to enquire.
          </p>

          <dl className="landing-appointment-info-list">
            <div className="landing-appointment-info-item">
              <dt>Prefer to call?</dt>
              <dd>
                <a className="landing-header-phone" href="tel:1300227432">
                  <IconPhone size={18} /> 1300 227 432
                </a>
              </dd>
            </div>
            <div className="landing-appointment-info-item">
              <dt>Response time</dt>
              <dd>We call back within one business day, Monday to Friday.</dd>
            </div>
            <div className="landing-appointment-info-item">
              <dt>Not sure what you need?</dt>
              <dd>Choose "General Enquiry" below and tell us in the message field.</dd>
            </div>
          </dl>
        </div>

        <div className="landing-form-panel">
          {submitted ? (
            <div className="landing-success-panel" role="status">
              <span className="landing-success-icon" aria-hidden="true">
                <IconCheck size={28} />
              </span>
              <h3 tabIndex={-1} ref={successHeadingRef}>
                Thanks, {values.full_name.split(" ")[0] || "your request is in"}. Your request has been received.
              </h3>
              <p>
                We'll call you on {values.phone} within one business day to confirm your
                appointment. A confirmation has also been sent to {values.email}.
              </p>
              <button type="button" className="landing-btn landing-btn-secondary" onClick={handleBookAnother}>
                Book another appointment
              </button>
            </div>
          ) : (
            <form noValidate onSubmit={handleSubmit}>
              <h3 className="landing-sr-only">Appointment request form</h3>

              {/* Honeypot. Hidden from sight and from screen readers, and
                  skipped by keyboard tabbing, so no real visitor can fill it
                  in; automated form-fillers populate every input they find.
                  A submission with this set is discarded server-side. */}
              <div className="landing-hp" aria-hidden="true">
                <label htmlFor="website">Website</label>
                <input
                  id="website"
                  name="website"
                  type="text"
                  tabIndex={-1}
                  autoComplete="off"
                  value={values.website}
                  onChange={(event) => setField("website", event.target.value)}
                />
              </div>

              {errorList.length > 0 && (
                <div
                  className="landing-error-summary"
                  role="alert"
                  tabIndex={-1}
                  ref={errorSummaryRef}
                >
                  <p className="landing-error-summary-title">
                    Please fix {errorList.length === 1 ? "this problem" : `these ${errorList.length} problems`}{" "}
                    before submitting:
                  </p>
                  <ul>
                    {errorList.map(([field, message]) => (
                      <li key={field}>
                        <a href={`#${field}`}>{message}</a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {submitError && (
                <p className="landing-submit-error" role="alert">
                  {submitError}
                </p>
              )}

              <div className="landing-form-row">
                <Field id="full_name" label="Full name" required error={errors.full_name}>
                  {(inputProps) => (
                    <input
                      {...inputProps}
                      className="landing-input"
                      type="text"
                      autoComplete="name"
                      value={values.full_name}
                      onChange={(e) => setField("full_name", e.target.value)}
                    />
                  )}
                </Field>

                <Field id="phone" label="Phone number" required error={errors.phone}>
                  {(inputProps) => (
                    <input
                      {...inputProps}
                      className="landing-input"
                      type="tel"
                      autoComplete="tel"
                      value={values.phone}
                      onChange={(e) => setField("phone", e.target.value)}
                    />
                  )}
                </Field>
              </div>

              <Field id="email" label="Email address" required error={errors.email}>
                {(inputProps) => (
                  <input
                    {...inputProps}
                    className="landing-input"
                    type="email"
                    autoComplete="email"
                    value={values.email}
                    onChange={(e) => setField("email", e.target.value)}
                  />
                )}
              </Field>

              <Field
                id="appointment_type"
                label="Service required"
                required
                error={errors.appointment_type}
              >
                {(inputProps) => (
                  <select
                    {...inputProps}
                    className="landing-select"
                    value={values.appointment_type}
                    onChange={(e) => setField("appointment_type", e.target.value)}
                  >
                    <option value="">Select a service…</option>
                    {APPOINTMENT_SERVICE_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                )}
              </Field>

              <div className="landing-form-row">
                <Field id="preferred_date" label="Preferred date" hint="Optional">
                  {(inputProps) => (
                    <input
                      {...inputProps}
                      className="landing-input"
                      type="date"
                      value={values.preferred_date}
                      onChange={(e) => setField("preferred_date", e.target.value)}
                    />
                  )}
                </Field>

                <Field id="preferred_time" label="Preferred time" hint="Optional">
                  {(inputProps) => (
                    <input
                      {...inputProps}
                      className="landing-input"
                      type="time"
                      value={values.preferred_time}
                      onChange={(e) => setField("preferred_time", e.target.value)}
                    />
                  )}
                </Field>
              </div>

              <Field id="message" label="Message" hint="Optional — tell us anything that will help">
                {(inputProps) => (
                  <textarea
                    {...inputProps}
                    className="landing-textarea"
                    value={values.message}
                    onChange={(e) => setField("message", e.target.value)}
                  />
                )}
              </Field>

              <div className="landing-field">
                <div className="landing-checkbox-field">
                  <input
                    id="consent"
                    type="checkbox"
                    checked={values.consent}
                    aria-invalid={errors.consent ? "true" : undefined}
                    aria-describedby={errors.consent ? "consent-error" : undefined}
                    onChange={(e) => setField("consent", e.target.checked)}
                  />
                  <label htmlFor="consent">
                    I agree to be contacted by CareOS about this enquiry.
                    <span className="landing-required" aria-hidden="true">
                      {" "}
                      *
                    </span>
                  </label>
                </div>
                {errors.consent && (
                  <span className="landing-field-error" id="consent-error" role="alert">
                    {errors.consent}
                  </span>
                )}
              </div>

              <button
                type="submit"
                className="landing-btn landing-btn-primary landing-btn-block"
                disabled={submitting}
                aria-busy={submitting}
              >
                {submitting && <span className="landing-spinner" aria-hidden="true" />}
                {submitting ? "Sending your request…" : "Request Appointment"}
              </button>
            </form>
          )}
        </div>
      </div>
    </section>
  );
}
