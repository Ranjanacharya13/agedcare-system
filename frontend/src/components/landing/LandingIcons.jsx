function Svg({ size = 24, children, ...rest }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...rest}
    >
      {children}
    </svg>
  );
}

export function IconArrowUp(props) {
  return (
    <Svg {...props}>
      <path d="M12 19V5" />
      <path d="m5 12 7-7 7 7" />
    </Svg>
  );
}

export function IconHome(props) {
  return (
    <Svg {...props}>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.8V21h14V9.8" />
      <path d="M10 21v-6h4v6" />
    </Svg>
  );
}

export function IconHeart(props) {
  return (
    <Svg {...props}>
      <path d="M12 20s-7.5-4.6-7.5-9.6A4.4 4.4 0 0 1 12 7.6a4.4 4.4 0 0 1 7.5 2.8C19.5 15.4 12 20 12 20Z" />
    </Svg>
  );
}

export function IconBrain(props) {
  return (
    <Svg {...props}>
      <path d="M12 5.5a3 3 0 0 0-5.7-1.3A2.8 2.8 0 0 0 4 9.4a3 3 0 0 0 .6 5A2.8 2.8 0 0 0 9 19.4a3 3 0 0 0 3-2.9Z" />
      <path d="M12 5.5a3 3 0 0 1 5.7-1.3A2.8 2.8 0 0 1 20 9.4a3 3 0 0 1-.6 5A2.8 2.8 0 0 1 15 19.4a3 3 0 0 1-3-2.9Z" />
    </Svg>
  );
}

export function IconStethoscope(props) {
  return (
    <Svg {...props}>
      <path d="M5 3v5a4 4 0 0 0 8 0V3" />
      <path d="M5 3H3.5M13 3h1.5" />
      <path d="M9 12v2a5 5 0 0 0 10 0v-1" />
      <circle cx="19" cy="10.5" r="2" />
    </Svg>
  );
}

export function IconActivity(props) {
  return (
    <Svg {...props}>
      <path d="M3 12h4l2.5-7 5 14L17 12h4" />
    </Svg>
  );
}

export function IconUsers(props) {
  return (
    <Svg {...props}>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3.5 20a5.5 5.5 0 0 1 11 0" />
      <path d="M16 5.5a3.2 3.2 0 0 1 0 5.9" />
      <path d="M17.5 14.4A5.5 5.5 0 0 1 20.5 20" />
    </Svg>
  );
}

export function IconFacebook(props) {
  return (
    <Svg {...props}>
      <path d="M14.5 8.5H17V5.4h-2.6c-2.1 0-3.4 1.4-3.4 3.5v1.6H8.5v3.1H11V21h3.2v-7.4h2.4l.4-3.1h-2.8V9.3c0-.5.2-.8.8-.8Z" />
    </Svg>
  );
}

export function IconLinkedIn(props) {
  return (
    <Svg {...props}>
      <rect x="3.5" y="3.5" width="17" height="17" rx="2.5" />
      <path d="M8 10.5V16" />
      <path d="M8 7.9v.1" />
      <path d="M11.8 16v-3.1a2 2 0 0 1 4 0V16" />
      <path d="M11.8 10.5V16" />
    </Svg>
  );
}

export function IconInstagram(props) {
  return (
    <Svg {...props}>
      <rect x="3.5" y="3.5" width="17" height="17" rx="4.5" />
      <circle cx="12" cy="12" r="3.6" />
      <path d="M16.9 7.1v.1" />
    </Svg>
  );
}

export function IconMapPin(props) {
  return (
    <Svg {...props}>
      <path d="M12 21s6.5-5.6 6.5-10.4A6.5 6.5 0 0 0 5.5 10.6C5.5 15.4 12 21 12 21Z" />
      <circle cx="12" cy="10.4" r="2.4" />
    </Svg>
  );
}
