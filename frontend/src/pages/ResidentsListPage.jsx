import { useNavigate } from "react-router-dom";
import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import { residentsConfig } from "../config/residents.config.js";

export default function ResidentsListPage() {
  const navigate = useNavigate();

  return (
    <div className="page">
      <h1 className="page-title">Residents</h1>
      <ResourcePanel resource={residentsConfig} onRowClick={(r) => navigate(`/admin/residents/${r.id}`)} />
    </div>
  );
}
