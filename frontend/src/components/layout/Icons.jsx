// Minimal hand-drawn stroke icon set (no icon library) — consistent 24x24
// viewBox, 1.8 stroke width, rounded joins.

const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

function Svg({ size = 20, children }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
      {children}
    </svg>
  );
}

export function IconDashboard(props) {
  return (
    <Svg {...props}>
      <rect x="3.5" y="3.5" width="7.5" height="7.5" rx="2" />
      <rect x="13" y="3.5" width="7.5" height="4.5" rx="2" />
      <rect x="13" y="10.5" width="7.5" height="10" rx="2" />
      <rect x="3.5" y="13.5" width="7.5" height="7" rx="2" />
    </Svg>
  );
}

export function IconResidents(props) {
  return (
    <Svg {...props}>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3.5 20c0-3.3 2.5-5.5 5.5-5.5s5.5 2.2 5.5 5.5" />
      <circle cx="17" cy="7" r="2.4" />
      <path d="M15.5 14.2c2.6.3 4.5 2.3 4.5 5" />
    </Svg>
  );
}

export function IconEmployees(props) {
  return (
    <Svg {...props}>
      <rect x="5" y="4.5" width="14" height="16" rx="2.5" />
      <circle cx="12" cy="10.5" r="2.3" />
      <path d="M8.2 17c.5-1.8 1.9-2.8 3.8-2.8s3.3 1 3.8 2.8" />
      <path d="M9.5 4.5V3.2h5v1.3" />
    </Svg>
  );
}

export function IconComplaints(props) {
  return (
    <Svg {...props}>
      <path d="M4 5.5h16v10.5H12.5L8 20v-4H4z" />
      <path d="M8 9.5h8M8 12.3h5" />
    </Svg>
  );
}

export function IconAlert(props) {
  return (
    <Svg {...props}>
      <path d="M12 3.5 21 19.5H3z" />
      <path d="M12 9.5v4.2" />
      <circle cx="12" cy="16.7" r="0.35" fill="currentColor" stroke="none" />
    </Svg>
  );
}

export function IconCalendar(props) {
  return (
    <Svg {...props}>
      <rect x="3.5" y="5" width="17" height="15" rx="2.2" />
      <path d="M3.5 9.5h17M8 3.2v3.2M16 3.2v3.2" />
      <circle cx="8.2" cy="13.2" r="0.9" fill="currentColor" stroke="none" />
      <circle cx="12" cy="13.2" r="0.9" fill="currentColor" stroke="none" />
      <circle cx="8.2" cy="16.6" r="0.9" fill="currentColor" stroke="none" />
    </Svg>
  );
}

export function IconClock(props) {
  return (
    <Svg {...props}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3.2 2" />
    </Svg>
  );
}

export function IconPulse(props) {
  return (
    <Svg {...props}>
      <path d="M3 12h4l2-6 4 12 2-6h6" />
    </Svg>
  );
}

export function IconChevronDown(props) {
  return (
    <Svg {...props}>
      <path d="M6 9l6 6 6-6" />
    </Svg>
  );
}
