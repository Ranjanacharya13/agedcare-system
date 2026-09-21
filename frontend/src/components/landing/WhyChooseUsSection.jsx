import { IconCheck } from "../layout/Icons.jsx";
import { WHY_CHOOSE_US_POINTS } from "../../config/landingContent.js";
import front2 from "../../images/front2.jpeg";

export default function WhyChooseUsSection() {
  return (
    <section id="about" className="landing-section">
      <div className="landing-container landing-why-inner">
        <div className="landing-why-media">
          <img
            src={front2}
            alt="A care worker walking arm in arm with an older woman through a garden"
          />
        </div>

        <div>
          <span className="landing-eyebrow">About CareOS</span>
          <h2 className="landing-section-title">Why families choose us</h2>
          <p className="landing-section-lead">
            We're a family-owned aged care provider, not a large chain. That shapes how we
            hire, how we roster staff, and how we talk with families.
          </p>

          <ul className="landing-why-list">
            {WHY_CHOOSE_US_POINTS.map((point) => (
              <li key={point} className="landing-why-item">
                <IconCheck size={22} />
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
