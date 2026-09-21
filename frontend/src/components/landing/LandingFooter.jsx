import { Link } from "react-router-dom";
import Logo from "../layout/Logo.jsx";
import { IconFacebook, IconLinkedIn, IconInstagram } from "./LandingIcons.jsx";

const QUICK_LINKS = [
  { href: "#services", label: "Our Services" },
  { href: "#about", label: "About Us" },
  { href: "#how-it-works", label: "How It Works" },
  { href: "#testimonials", label: "Family Stories" },
  { href: "#faq", label: "FAQ" },
];

const SUPPORT_LINKS = [
  { href: "#appointment", label: "Book an Appointment" },
  { href: "#appointment", label: "Request a Call Back" },
  { href: "#contact", label: "Careers at CareOS" },
  { href: "#appointment", label: "Feedback & Complaints" },
  { href: "#faq", label: "Fees & Funding" },
];

export default function LandingFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="landing-footer">
      <div className="landing-container">
        <div className="landing-footer-grid">
          <div>
            <Logo tone="dark" size={42} />
            <p className="landing-footer-about">
              CareOS is a family-owned aged care provider offering residential care, respite stays
              and in-home support, built around getting to know each resident personally.
            </p>
            <div className="landing-footer-social">
              <a href="#top" aria-label="CareOS on Facebook">
                <IconFacebook size={20} />
              </a>
              <a href="#top" aria-label="CareOS on LinkedIn">
                <IconLinkedIn size={20} />
              </a>
              <a href="#top" aria-label="CareOS on Instagram">
                <IconInstagram size={20} />
              </a>
            </div>
          </div>

          <div>
            <h3 className="landing-footer-heading">Explore</h3>
            <ul className="landing-footer-links">
              {QUICK_LINKS.map((link) => (
                <li key={link.label}>
                  <a href={link.href}>{link.label}</a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="landing-footer-heading">Get involved</h3>
            <ul className="landing-footer-links">
              {SUPPORT_LINKS.map((link) => (
                <li key={link.label}>
                  <a href={link.href}>{link.label}</a>
                </li>
              ))}
            </ul>
          </div>

          <div id="contact">
            <h3 className="landing-footer-heading">Visit or contact us</h3>
            <dl className="landing-footer-contact">
              <dt>Phone</dt>
              <dd>
                <a href="tel:1300227432">1300 227 432</a>
              </dd>
              <dt>Email</dt>
              <dd>
                <a href="mailto:hello@careos-agedcare.example">hello@careos-agedcare.example</a>
              </dd>
              <dt>Address</dt>
              <dd>24 Wattle Grove, Blackwood SA 5051</dd>
              <dt>Office hours</dt>
              <dd>Mon&ndash;Fri, 8am&ndash;6pm. Care staff on site 24/7.</dd>
            </dl>
          </div>
        </div>

        <p className="landing-footer-statement">
          CareOS acknowledges the Traditional Owners of the lands on which we live and work, and
          pays respect to Elders past and present. We welcome residents, families and staff of
          every background, and we are committed to care that is safe, respectful and free from
          discrimination.
        </p>

        <div className="landing-footer-bottom">
          <span>&copy; {year} CareOS Aged Care. All rights reserved.</span>
          <Link to="/admin">Staff Portal</Link>
        </div>
      </div>
    </footer>
  );
}
