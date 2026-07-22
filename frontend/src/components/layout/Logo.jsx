export default function Logo({ size = 34, withWordmark = true, tone = "light" }) {
  return (
    <span className="logo">
      <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
        <defs>
          <linearGradient id="logoBg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#95bdd7" />
            <stop offset="100%" stopColor="#375f82" />
          </linearGradient>
        </defs>
        <rect width="32" height="32" rx="10" fill="url(#logoBg)" />
        {/* Kangaroo silhouette mascot mark -- sand-yellow against the ocean
            badge for a bit of Aussie beach-at-dusk contrast. */}
        <g fill="var(--color-sand)">
          <ellipse cx="9" cy="23" rx="6" ry="2.6" transform="rotate(-30 9 23)" />
          <ellipse cx="17" cy="18" rx="6.5" ry="8" transform="rotate(-12 17 18)" />
          <rect x="15.5" y="14" width="2" height="5" rx="1" transform="rotate(15 16.5 16.5)" />
          <ellipse cx="23" cy="25.5" rx="5.5" ry="2.6" transform="rotate(-8 23 25.5)" />
          <ellipse cx="27.3" cy="25" rx="1.4" ry="1" />
          <circle cx="21.5" cy="9" r="3.6" />
          <ellipse cx="23.3" cy="5.3" rx="1.3" ry="2.4" transform="rotate(20 23.3 5.3)" />
          <ellipse cx="24.6" cy="10.2" rx="1.6" ry="1.2" />
        </g>
      </svg>
      {withWordmark && <span className={`logo-wordmark logo-wordmark-${tone}`}>CareOS</span>}
    </span>
  );
}
