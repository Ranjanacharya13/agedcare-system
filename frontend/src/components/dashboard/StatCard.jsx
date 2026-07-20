export default function StatCard({ icon, label, value, tone = "primary" }) {
  return (
    <div className="stat-card fade-slide-in">
      <div className={`stat-card-icon stat-card-icon-${tone}`}>{icon}</div>
      <div>
        <div className="stat-card-value">{value}</div>
        <div className="stat-card-label">{label}</div>
      </div>
    </div>
  );
}
