import DashboardStats from "../components/dashboard/DashboardStats.jsx";
import RiskScoreLeaderboard from "../components/dashboard/RiskScoreLeaderboard.jsx";
import UpcomingShifts from "../components/dashboard/UpcomingShifts.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { IconKangaroo } from "../components/layout/Icons.jsx";

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { user } = useAuth();
  const today = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="page">
      <div className="dashboard-hero fade-slide-in">
        <IconKangaroo size={140} className="dashboard-hero-mascot" />
        <p className="dashboard-hero-eyebrow">{today}</p>
        <h1 className="page-title dashboard-hero-title">
          {greeting()}
          {user?.name ? `, ${user.name}` : ""}
        </h1>
        <p className="text-muted">Here's what's happening across the facility today.</p>
      </div>
      <DashboardStats />
      <div className="dashboard-grid">
        <RiskScoreLeaderboard />
        <UpcomingShifts />
      </div>
    </div>
  );
}
