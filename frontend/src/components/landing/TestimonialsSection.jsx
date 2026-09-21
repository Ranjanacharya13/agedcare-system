import { TESTIMONIALS } from "../../config/landingContent.js";

function initialsOf(name) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

export default function TestimonialsSection() {
  return (
    <section id="testimonials" className="landing-section landing-section-alt">
      <div className="landing-container">
        <div className="landing-section-header">
          <span className="landing-eyebrow">In their words</span>
          <h2 className="landing-section-title">What families tell us</h2>
        </div>

        <div className="landing-testimonials-grid">
          {TESTIMONIALS.map((testimonial) => (
            <figure key={testimonial.name} className="landing-testimonial">
              <span className="landing-testimonial-mark" aria-hidden="true">
                &ldquo;
              </span>
              <blockquote className="landing-testimonial-quote">{testimonial.quote}</blockquote>
              <figcaption className="landing-testimonial-attribution">
                <span className="landing-testimonial-avatar" aria-hidden="true">
                  {initialsOf(testimonial.name)}
                </span>
                <span>
                  <span className="landing-testimonial-name">{testimonial.name}</span>
                  <br />
                  <span className="landing-testimonial-relationship">
                    {testimonial.relationship}
                  </span>
                </span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
