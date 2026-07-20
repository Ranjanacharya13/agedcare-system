import { useState } from "react";
import Button from "../common/Button.jsx";
import Modal from "../common/Modal.jsx";
import ResourceForm from "../resource/ResourceForm.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import { createResourceApi } from "../../api/resourceApi.js";
import { employeesConfig } from "../../config/employees.config.js";
import { formatDate, initials } from "../../utils/format.js";

const employeesApi = createResourceApi(employeesConfig);

export default function EmployeeHeaderCard({ employee, onUpdated }) {
  const [editing, setEditing] = useState(false);

  const handleSubmit = async (values) => {
    const updated = await employeesApi.update(employee.id, values);
    onUpdated(updated);
    setEditing(false);
  };

  return (
    <div className="header-card fade-slide-in">
      <div className="header-card-body">
        <div className="avatar">{initials(employee.first_name, employee.last_name)}</div>
        <div className="header-card-main">
          <h1>
            {employee.first_name} {employee.last_name}
          </h1>
          <div className="header-card-meta">
            <span>{employee.role || "No role set"}</span>
            <span>{employee.employment_status || "—"}</span>
            <span>Hired {formatDate(employee.hire_date)}</span>
            {!employee.active && <StatusBadge value="Inactive" badgeKind="verified" />}
          </div>
          <p className="text-muted">
            {employee.email || "No email"} {employee.phone && `— ${employee.phone}`}
          </p>
        </div>
      </div>
      <Button variant="secondary" size="sm" onClick={() => setEditing(true)}>
        Edit
      </Button>

      {editing && (
        <Modal title="Edit Employee" onClose={() => setEditing(false)}>
          <ResourceForm
            resource={employeesConfig}
            record={employee}
            onSubmit={handleSubmit}
            onCancel={() => setEditing(false)}
          />
        </Modal>
      )}
    </div>
  );
}
