import { IMPACT_STATS } from "../../config/landingContent.js";

export default function ImpactStats() {
  return (
    <section className="landing-impact" aria-label="CareOS at a glance">
      <div className="landing-container">
        <ul className="landing-impact-list">
          {IMPACT_STATS.map((stat) => (
            <li key={stat.label} className="landing-impact-item">
              <span className="landing-impact-value">{stat.value}</span>
              <span className="landing-impact-label">{stat.label}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
