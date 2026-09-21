import StatCard from "./StatCard.jsx";
import { useDirectory } from "../../hooks/useDirectory.js";
import { useAsync } from "../../hooks/useAsync.js";
import { get } from "../../api/client.js";
import { IconResidents, IconEmployees, IconComplaints } from "../layout/Icons.jsx";
import Skeleton from "../common/Skeleton.jsx";

export default function DashboardStats() {
  const { residents, employees, loading: directoryLoading } = useDirectory();
  const { data: complaints, loading: complaintsLoading } = useAsync(
    () => get("/complaints?skip=0&limit=1000"),
    []
  );

  const loading = directoryLoading || complaintsLoading;
  if (loading) return <Skeleton rows={2} />;

  const openComplaints = (complaints || []).filter((c) => c.status === "Open").length;

  return (
    <div className="stat-grid">
      <StatCard
        icon={<IconResidents size={20} />}
        label="Residents"
        value={residents.length}
        tone="primary"
        to="/admin/residents"
      />
      <StatCard
        icon={<IconEmployees size={20} />}
        label="Employees"
        value={employees.length}
        tone="secondary"
        to="/admin/employees"
      />
      <StatCard
        icon={<IconComplaints size={20} />}
        label="Open Complaints"
        value={openComplaints}
        tone="info"
        to="/admin/complaints"
      />
    </div>
  );
}
