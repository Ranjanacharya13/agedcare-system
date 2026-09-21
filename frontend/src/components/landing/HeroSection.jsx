import { IconPhone } from "../layout/Icons.jsx";
import front1 from "../../images/front1.jpg";

const PHONE_NUMBER = "1300 227 432";

export default function HeroSection() {
  return (
    <section id="top" className="landing-hero">
      <div className="landing-container landing-hero-inner">
        <div>
          <span className="landing-hero-eyebrow">Aged care, done personally</span>
          <h1 className="landing-hero-title">Wherever life takes you, we're here</h1>
          <p className="landing-hero-lead">
            CareOS provides residential, respite and in-home aged care with a small-team, family
            feel. Real people answer the phone, and you'll always know who's looking after your
            family member.
          </p>
          <div className="landing-hero-actions">
            <a className="landing-btn landing-btn-primary" href="#appointment">
              Book an Appointment
            </a>
            <a className="landing-btn landing-btn-ghost-light" href="#services">
              See Our Services
            </a>
          </div>
          <a
            className="landing-hero-phone"
            href={`tel:${PHONE_NUMBER.replace(/\s/g, "")}`}
          >
            <IconPhone size={22} />
            Prefer to talk? Call {PHONE_NUMBER}
          </a>
        </div>

        <div className="landing-hero-media">
          <img
            src={front1}
            alt="A care worker leaning down to smile and talk with an older man relaxing on a couch at home"
          />
          <p className="landing-hero-badge">
            <strong>One coordinator per resident</strong>
            So you always know exactly who to call, by name.
          </p>
        </div>
      </div>
    </section>
  );
}
