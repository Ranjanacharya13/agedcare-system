import DashboardStats from "../components/dashboard/DashboardStats.jsx";
import RiskScoreLeaderboard from "../components/dashboard/RiskScoreLeaderboard.jsx";
import UpcomingShifts from "../components/dashboard/UpcomingShifts.jsx";

export default function DashboardPage() {
  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>
      <DashboardStats />
      <div className="dashboard-grid">
        <RiskScoreLeaderboard />
        <UpcomingShifts />
      </div>
    </div>
  );
}
