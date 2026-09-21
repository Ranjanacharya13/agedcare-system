import { IconArrowUpRight } from "../layout/Icons.jsx";
import {
  IconHome,
  IconHeart,
  IconBrain,
  IconStethoscope,
  IconActivity,
  IconUsers,
} from "./LandingIcons.jsx";
import { SERVICES } from "../../config/landingContent.js";

const SERVICE_ICONS = {
  "residential-care": IconHome,
  "respite-care": IconHeart,
  "dementia-care": IconBrain,
  "nursing-care": IconStethoscope,
  "allied-health": IconActivity,
  "family-support": IconUsers,
};

export default function ServicesSection() {
  return (
    <section id="services" className="landing-section">
      <div className="landing-container">
        <div className="landing-section-header">
          <span className="landing-eyebrow">Our services</span>
          <h2 className="landing-section-title">Care that fits your family's situation</h2>
          <p className="landing-section-lead">
            Every family's needs are different. Here's what we offer, in plain terms.
          </p>
        </div>

        <div className="landing-services-grid">
          {SERVICES.map((service) => {
            const Icon = SERVICE_ICONS[service.id] ?? IconHeart;
            return (
              <article key={service.id} className="landing-service-card">
                <span className="landing-service-icon">
                  <Icon size={26} />
                </span>
                <h3 className="landing-service-title">{service.title}</h3>
                <p className="landing-service-description">{service.description}</p>
                <span className="landing-service-link">
                  <a className="landing-arrow-link" href="#appointment">
                    Enquire about this
                    <IconArrowUpRight size={18} />
                    <span className="landing-sr-only"> — {service.title}</span>
                  </a>
                </span>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
