import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import { appointmentsConfig } from "../config/appointments.config.js";

export default function AppointmentsPage() {
  return (
    <div className="page">
      <h1 className="page-title">Appointments</h1>
      <ResourcePanel resource={appointmentsConfig} />
    </div>
  );
}
