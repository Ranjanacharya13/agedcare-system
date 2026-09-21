import "../styles/landing.css";
import LandingHeader from "../components/landing/LandingHeader.jsx";
import HeroSection from "../components/landing/HeroSection.jsx";
import ImpactStats from "../components/landing/ImpactStats.jsx";
import TrustIndicators from "../components/landing/TrustIndicators.jsx";
import ServicesSection from "../components/landing/ServicesSection.jsx";
import HowItWorksSection from "../components/landing/HowItWorksSection.jsx";
import WhyChooseUsSection from "../components/landing/WhyChooseUsSection.jsx";
import TestimonialsSection from "../components/landing/TestimonialsSection.jsx";
import FaqSection from "../components/landing/FaqSection.jsx";
import AppointmentSection from "../components/landing/AppointmentSection.jsx";
import LandingFooter from "../components/landing/LandingFooter.jsx";
import StickyBookButton from "../components/landing/StickyBookButton.jsx";
import BackToTop from "../components/landing/BackToTop.jsx";

export default function PublicLandingPage() {
  return (
    <div className="landing landing-has-sticky-cta">
      <a className="landing-skip-link" href="#main-content">
        Skip to main content
      </a>

      <LandingHeader />

      <main id="main-content">
        <HeroSection />
        <ImpactStats />
        <TrustIndicators />
        <ServicesSection />
        <HowItWorksSection />
        <WhyChooseUsSection />
        <TestimonialsSection />
        <FaqSection />
        <AppointmentSection />
      </main>

      <LandingFooter />
      <StickyBookButton />
      <BackToTop />
    </div>
  );
}
