import { useNavigate } from "react-router-dom";
import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import { employeesConfig } from "../config/employees.config.js";

export default function EmployeesListPage() {
  const navigate = useNavigate();

  return (
    <div className="page">
      <h1 className="page-title">Employees</h1>
      <ResourcePanel resource={employeesConfig} onRowClick={(e) => navigate(`/admin/employees/${e.id}`)} />
    </div>
  );
}
