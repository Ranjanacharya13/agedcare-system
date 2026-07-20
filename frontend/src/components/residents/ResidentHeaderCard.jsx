import { useState } from "react";
import Button from "../common/Button.jsx";
import Modal from "../common/Modal.jsx";
import ResourceForm from "../resource/ResourceForm.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import { createResourceApi } from "../../api/resourceApi.js";
import { residentsConfig } from "../../config/residents.config.js";
import { formatDate, initials } from "../../utils/format.js";

const residentsApi = createResourceApi(residentsConfig);

export default function ResidentHeaderCard({ resident, onUpdated }) {
  const [editing, setEditing] = useState(false);

  const handleSubmit = async (values) => {
    const updated = await residentsApi.update(resident.id, values);
    onUpdated(updated);
    setEditing(false);
  };

  return (
    <div className="header-card fade-slide-in">
      <div className="header-card-body">
        <div className="avatar">{initials(resident.first_name, resident.last_name)}</div>
        <div className="header-card-main">
          <h1>
            {resident.first_name} {resident.last_name}
          </h1>
          <div className="header-card-meta">
            <span>Room {resident.room_number || "—"}</span>
            <span>DOB {formatDate(resident.dob)}</span>
            <StatusBadge value={resident.cognitive_status} />
            {!resident.active && <StatusBadge value="Inactive" badgeKind="verified" />}
          </div>
          {resident.emergency_contact?.name && (
            <p className="text-muted">
              Emergency contact: {resident.emergency_contact.name}
              {resident.emergency_contact.relationship && ` (${resident.emergency_contact.relationship})`}
              {resident.emergency_contact.phone && ` — ${resident.emergency_contact.phone}`}
            </p>
          )}
        </div>
      </div>
      <Button variant="secondary" size="sm" onClick={() => setEditing(true)}>
        Edit
      </Button>

      {editing && (
        <Modal title="Edit Resident" onClose={() => setEditing(false)}>
          <ResourceForm
            resource={residentsConfig}
            record={resident}
            onSubmit={handleSubmit}
            onCancel={() => setEditing(false)}
          />
        </Modal>
      )}
    </div>
  );
}
