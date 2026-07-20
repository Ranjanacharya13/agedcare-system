export default function Logo({ size = 34, withWordmark = true, tone = "light" }) {
  return (
    <span className="logo">
      <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
        <defs>
          <linearGradient id="logoBg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#14b8a6" />
            <stop offset="100%" stopColor="#0f766e" />
          </linearGradient>
        </defs>
        <rect width="32" height="32" rx="10" fill="url(#logoBg)" />
        <path
          d="M16 24.5s-7.5-4.3-7.5-10A4 4 0 0 1 16 12a4 4 0 0 1 7.5 2.5c0 5.7-7.5 10-7.5 10z"
          fill="var(--color-secondary)"
        />
      </svg>
      {withWordmark && <span className={`logo-wordmark logo-wordmark-${tone}`}>CareOS</span>}
    </span>
  );
}
