import { useAsync } from "../../hooks/useAsync.js";
import { getResidentRiskScore } from "../../api/riskScores.js";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";
import StatusBadge from "../common/StatusBadge.jsx";

export default function RiskScoreCard({ residentId }) {
  const { data, loading, error } = useAsync(() => getResidentRiskScore(residentId), [residentId]);

  if (loading) return <Skeleton rows={5} />;
  if (error) return <ErrorBanner error={error} />;
  if (!data) return null;

  return (
    <div className="risk-score-card fade-slide-in">
      <div className="risk-score-summary">
        <div className="risk-score-ring">
          <span className="risk-score-number">{data.score}</span>
        </div>
        <div>
          <StatusBadge value={data.band} badgeKind="riskBand" />
          <p className="text-muted" style={{ margin: "var(--space-1) 0 0" }}>
            Out of a possible 100 points.
          </p>
        </div>
      </div>
      <table className="breakdown-table">
        <thead>
          <tr>
            <th>Signal</th>
            <th>Observed</th>
            <th>Points</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.breakdown).map(([key, item]) => (
            <tr key={key}>
              <td>{key.replaceAll("_", " ")}</td>
              <td>{item.value}</td>
              <td>{item.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
