import StatCard from "./StatCard.jsx";
import { useDirectory } from "../../hooks/useDirectory.js";
import { useAsync } from "../../hooks/useAsync.js";
import { getRiskScores } from "../../api/riskScores.js";
import { get } from "../../api/client.js";
import { IconResidents, IconEmployees, IconAlert, IconComplaints } from "../layout/Icons.jsx";
import Skeleton from "../common/Skeleton.jsx";

export default function DashboardStats() {
  const { residents, employees, loading: directoryLoading } = useDirectory();
  const { data: riskScores, loading: riskLoading } = useAsync(() => getRiskScores(), []);
  const { data: complaints, loading: complaintsLoading } = useAsync(
    () => get("/complaints?skip=0&limit=1000"),
    []
  );

  const loading = directoryLoading || riskLoading || complaintsLoading;
  if (loading) return <Skeleton rows={2} />;

  const highPriority = (riskScores || []).filter(
    (r) => r.band === "Critical" || r.band === "High"
  ).length;
  const openComplaints = (complaints || []).filter((c) => c.status === "Open").length;

  return (
    <div className="stat-grid">
      <StatCard icon={<IconResidents size={20} />} label="Residents" value={residents.length} tone="primary" />
      <StatCard icon={<IconEmployees size={20} />} label="Employees" value={employees.length} tone="secondary" />
      <StatCard icon={<IconAlert size={20} />} label="High Priority Residents" value={highPriority} tone="danger" />
      <StatCard icon={<IconComplaints size={20} />} label="Open Complaints" value={openComplaints} tone="info" />
    </div>
  );
}
