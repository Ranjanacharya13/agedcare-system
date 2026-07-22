import { Link } from "react-router-dom";
import { IconArrowUpRight } from "../layout/Icons.jsx";

export default function StatCard({ icon, label, value, tone = "primary", to }) {
  const content = (
    <>
      <div className={`stat-card-icon stat-card-icon-${tone}`}>{icon}</div>
      <div className="stat-card-body">
        <div className="stat-card-value">{value}</div>
        <div className="stat-card-label">{label}</div>
      </div>
      {to && (
        <span className="stat-card-arrow" aria-hidden="true">
          <IconArrowUpRight size={16} />
        </span>
      )}
    </>
  );

  if (to) {
    return (
      <Link to={to} className="stat-card stat-card-link fade-slide-in">
        {content}
      </Link>
    );
  }

  return <div className="stat-card fade-slide-in">{content}</div>;
}
