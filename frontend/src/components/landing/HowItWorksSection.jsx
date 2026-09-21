import { HOW_IT_WORKS_STEPS } from "../../config/landingContent.js";

export default function HowItWorksSection() {
  return (
    <section id="how-it-works" className="landing-section landing-section-warm">
      <div className="landing-container">
        <div className="landing-section-header">
          <span className="landing-eyebrow">How it works</span>
          <h2 className="landing-section-title">Four steps, no surprises</h2>
          <p className="landing-section-lead">
            We keep the process simple and explain everything along the way.
          </p>
        </div>

        <ol className="landing-steps">
          {HOW_IT_WORKS_STEPS.map((step, index) => (
            <li key={step.title} className="landing-step">
              <span className="landing-step-number" aria-hidden="true">
                {index + 1}
              </span>
              <h3 className="landing-step-title">
                <span className="landing-sr-only">Step {index + 1}: </span>
                {step.title}
              </h3>
              <p className="landing-step-description">{step.description}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
