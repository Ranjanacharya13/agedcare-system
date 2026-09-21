import { Link } from "react-router-dom";
import { formatDate } from "../../utils/format.js";
import { ageFromDob } from "../../utils/residentTone.js";

/** Key facts at a glance, plus the two things staff most often want next. */
export default function ResidentOverview({ resident, baseUrl }) {
  const age = ageFromDob(resident.dob);
  const contact = resident.emergency_contact;
  const facts = [
    ["Room", resident.room_number || "—"],
    ["Age", age !== null ? `${age} years` : "—"],
    ["Date of birth", formatDate(resident.dob)],
    ["Gender", resident.gender || "—"],
    ["Admitted", formatDate(resident.admission_date)],
    ["Cognitive status", resident.cognitive_status || "—"],
  ];

  return (
    <div className="overview">
      <dl className="fact-grid">
        {facts.map(([label, value]) => (
          <div key={label} className="fact">
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      {contact?.name && (
        <div className="overview-card">
          <h3 className="section-title">Emergency contact</h3>
          <p>
            <strong>{contact.name}</strong>
            {contact.relationship && ` (${contact.relationship})`}
          </p>
          <p className="text-muted">
            {[contact.phone, contact.email].filter(Boolean).join(" · ") || "No contact details"}
          </p>
        </div>
      )}

      <div className="overview-links">
        <Link className="btn btn-secondary btn-sm" to={`${baseUrl}/care-team`}>
          Who cares for {resident.first_name}?
        </Link>
      </div>
    </div>
  );
}
