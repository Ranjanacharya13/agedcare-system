import { Link } from "react-router-dom";
import { useAsync } from "../../hooks/useAsync.js";
import { getRiskScores } from "../../api/riskScores.js";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import EmptyState from "../common/EmptyState.jsx";
import StatusBadge from "../common/StatusBadge.jsx";

export default function RiskScoreLeaderboard() {
  const { data, loading, error } = useAsync(() => getRiskScores(), []);

  return (
    <section className="card fade-slide-in">
      <h2>Resident Priority</h2>
      <p className="text-muted">Ranked by risk score — highest first.</p>
      <ErrorBanner error={error} />
      {loading ? (
        <Skeleton rows={4} />
      ) : !data?.length ? (
        <EmptyState message="No residents yet." />
      ) : (
        <ol className="leaderboard">
          {data.slice(0, 10).map((entry, index) => (
            <li key={entry.resident_id} className="leaderboard-row">
              <span className="leaderboard-rank">{index + 1}</span>
              <div className="leaderboard-main">
                <Link to={`/admin/residents/${entry.resident_id}/risk-score`} className="leaderboard-name">
                  {entry.first_name} {entry.last_name}
                </Link>
                <div className="leaderboard-bar-track">
                  <div
                    className={`leaderboard-bar-fill leaderboard-bar-${(entry.band || "low").toLowerCase()}`}
                    style={{ width: `${Math.min(Math.max(entry.score, 0), 100)}%` }}
                  />
                </div>
              </div>
              <span className="leaderboard-score">{entry.score}</span>
              <StatusBadge value={entry.band} badgeKind="riskBand" />
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
