import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import { complaintsConfig } from "../config/complaints.config.js";

export default function ComplaintsPage() {
  return (
    <div className="page">
      <h1 className="page-title">Complaints & Feedback</h1>
      <ResourcePanel resource={complaintsConfig} />
    </div>
  );
}
