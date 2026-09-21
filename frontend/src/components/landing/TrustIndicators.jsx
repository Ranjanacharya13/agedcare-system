import { IconCheck } from "../layout/Icons.jsx";
import { TRUST_INDICATORS } from "../../config/landingContent.js";

export default function TrustIndicators() {
  return (
    <div className="landing-trust">
      <div className="landing-container">
        <ul className="landing-trust-list">
          {TRUST_INDICATORS.map((item) => (
            <li key={item} className="landing-trust-item">
              <IconCheck size={20} />
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
