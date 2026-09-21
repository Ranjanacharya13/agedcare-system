import { IconChevronDown } from "../layout/Icons.jsx";
import { FAQS } from "../../config/landingContent.js";

export default function FaqSection() {
  return (
    <section id="faq" className="landing-section">
      <div className="landing-container">
        <div className="landing-section-header">
          <span className="landing-eyebrow">Frequently asked questions</span>
          <h2 className="landing-section-title">Common questions from families</h2>
        </div>

        <div className="landing-faq-list">
          {FAQS.map((faq) => (
            <details key={faq.question} className="landing-faq-item">
              <summary className="landing-faq-question">
                {faq.question}
                <IconChevronDown size={22} />
              </summary>
              <p className="landing-faq-answer">{faq.answer}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
