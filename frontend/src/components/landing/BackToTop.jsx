import { useEffect, useState } from "react";
import { IconArrowUp } from "./LandingIcons.jsx";

export default function BackToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 600);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!visible) return null;

  return (
    <button
      type="button"
      className="landing-back-to-top"
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
    >
      <IconArrowUp size={22} />
      <span className="landing-sr-only">Back to top</span>
    </button>
  );
}
