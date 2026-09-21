import { useState } from "react";
import { Link } from "react-router-dom";
import Logo from "../layout/Logo.jsx";
import { IconMenu, IconClose, IconPhone } from "../layout/Icons.jsx";

const NAV_LINKS = [
  { href: "#services", label: "Our Services" },
  { href: "#about", label: "About Us" },
  { href: "#how-it-works", label: "How It Works" },
  { href: "#testimonials", label: "Families" },
  { href: "#contact", label: "Contact" },
];

const UTILITY_LINKS = [
  { href: "#faq", label: "FAQ" },
  { href: "#appointment", label: "Feedback" },
  { href: "#contact", label: "Careers" },
];

const PHONE_NUMBER = "1300 227 432";
const PHONE_HREF = `tel:${PHONE_NUMBER.replace(/\s/g, "")}`;

export default function LandingHeader() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <div className="landing-utility-bar">
        <div className="landing-container landing-utility-inner">
          {UTILITY_LINKS.map((link) => (
            <a key={link.label} className="landing-utility-link" href={link.href}>
              {link.label}
            </a>
          ))}
          <Link className="landing-utility-link" to="/admin">
            Staff Portal
          </Link>
        </div>
      </div>

      <header className="landing-header">
        <div className="landing-container landing-header-inner">
          <a href="#top" aria-label="CareOS home">
            <Logo tone="light" size={42} />
          </a>

          <nav className="landing-nav" aria-label="Primary">
            <ul className="landing-nav-links">
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <a className="landing-nav-link" href={link.href}>
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <div className="landing-header-actions">
            <a className="landing-header-phone landing-header-phone-desktop" href={PHONE_HREF}>
              <IconPhone size={20} />
              {PHONE_NUMBER}
            </a>
            <a className="landing-btn landing-btn-primary" href="#appointment">
              Book Appointment
            </a>
            <button
              type="button"
              className="landing-nav-toggle"
              aria-expanded={menuOpen}
              aria-controls="landing-mobile-nav"
              onClick={() => setMenuOpen((open) => !open)}
            >
              {menuOpen ? <IconClose size={22} /> : <IconMenu size={22} />}
              <span className="landing-sr-only">{menuOpen ? "Close menu" : "Open menu"}</span>
            </button>
          </div>
        </div>

        <div id="landing-mobile-nav" className={`landing-nav-mobile${menuOpen ? " is-open" : ""}`}>
          <div className="landing-container">
            <ul className="landing-nav-mobile-links">
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <a
                    className="landing-nav-mobile-link"
                    href={link.href}
                    onClick={() => setMenuOpen(false)}
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
            <a className="landing-header-phone" href={PHONE_HREF}>
              <IconPhone size={20} />
              Call {PHONE_NUMBER}
            </a>
          </div>
        </div>
      </header>
    </>
  );
}
