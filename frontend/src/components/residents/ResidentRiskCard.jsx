import { useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { useAsync } from "../../hooks/useAsync.js";
import { getResidentRiskScore } from "../../api/algorithms.js";
import StatusBadge from "../common/StatusBadge.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

const CRITERIA_ORDER = [
  { key: "fall_risk", label: "Fall Risk", maxPts: 34, policy: "34% (Primary physical hazard)" },
  { key: "recent_incidents", label: "Recent Incidents", maxPts: 26, policy: "26% (SIRS reportable events)" },
  { key: "assistance_level", label: "Assistance Level", maxPts: 18, policy: "18% (AN-ACC mobility dependency)" },
  { key: "cognitive_status", label: "Cognitive Status", maxPts: 14, policy: "14% (Dementia impairment)" },
  { key: "recent_behaviour", label: "Recent Behaviour", maxPts: 8, policy: "8% (BPSD symptoms)" },
];

export default function ResidentRiskCard({ residentId }) {
  const { can } = useAuth();
  const [showDetails, setShowDetails] = useState(false);

  const { data, loading, error } = useAsync(
    (signal) => getResidentRiskScore(residentId, { signal }),
    [residentId]
  );

  if (!can("analytics", "read")) return null;
  if (loading) return <Skeleton rows={3} />;
  if (error) return <ErrorBanner error={error} />;
  if (!data) return null;

  const bandTone = (data.band || "Low").toLowerCase();

  return (
    <div className="overview-card risk-card">
      <div className="risk-card-header">
        <div>
          <h3 className="section-title">Clinical Risk Assessment</h3>
          <p className="text-muted algo-subtle">Simple Additive Weighting (SAW) Model</p>
        </div>
        <StatusBadge value={data.band} badgeKind="riskBand" />
      </div>

      <div className="risk-score-overview">
        <div className="risk-score-dial">
          <span className="risk-score-number">{data.score}</span>
          <span className="risk-score-max">/ 100</span>
        </div>
        <div className="risk-score-progress-wrap">
          <div className="risk-meter-track" role="progressbar" aria-valuenow={data.score} aria-valuemin="0" aria-valuemax="100">
            <div
              className={`risk-meter-fill risk-meter-${bandTone}`}
              style={{ width: `${Math.min(data.score, 100)}%` }}
            />
          </div>
          <span className="algo-subtle">
            Risk band: <strong>{data.band}</strong> (Low &lt;25, Med 25–49, High 50–74, Critical &ge;75)
          </span>
        </div>
      </div>

      <div className="risk-breakdown-section">
        <div className="risk-breakdown-header">
          <span className="text-muted" style={{ fontSize: "var(--font-size-xs)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            SAW Criteria Breakdown ({data.score} pts total)
          </span>
          <button
            type="button"
            className="btn-link"
            style={{ fontSize: "var(--font-size-xs)" }}
            onClick={() => setShowDetails((prev) => !prev)}
          >
            {showDetails ? "Hide breakdown" : "Show breakdown"}
          </button>
        </div>

        {showDetails && (
          <div className="risk-breakdown-list">
            {CRITERIA_ORDER.map(({ key, label, maxPts, policy }) => {
              const item = data.breakdown?.[key];
              if (!item) return null;
              const percentOfCriterion = Math.round(item.normalised * 100);

              return (
                <div key={key} className="risk-breakdown-row">
                  <div className="risk-breakdown-info">
                    <span className="risk-breakdown-label">
                      <strong>{label}</strong>
                      <span className="algo-subtle"> &mdash; {item.value}</span>
                    </span>
                    <span className="risk-breakdown-policy">{policy}</span>
                  </div>

                  <div className="risk-breakdown-bar-wrap">
                    <div className="risk-sub-track">
                      <div
                        className={`risk-sub-fill risk-sub-${bandTone}`}
                        style={{ width: `${percentOfCriterion}%` }}
                      />
                    </div>
                    <span className="risk-breakdown-pts">
                      <strong>{item.points}</strong> <small className="text-muted">/ {maxPts} pts</small>
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <details className="weight-disclosure" style={{ marginTop: "var(--space-3)" }}>
        <summary>Australian Clinical Policy Details (ACQSC &amp; SIRS)</summary>
        <p className="text-muted algo-subtle" style={{ marginTop: "var(--space-2)", lineHeight: 1.5 }}>
          Weights follow the SMART methodology aligned with Australian Aged Care Quality Standard 3 (Clinical Care)
          and Serious Incident Response Scheme (SIRS) adverse event priorities: Falls (34%), Incidents (26%), Transfer Assistance (18%),
          Cognitive Status (14%), and Behaviour (8%). Points add up directly to the 0–100 score.
        </p>
      </details>
    </div>
  );
}
