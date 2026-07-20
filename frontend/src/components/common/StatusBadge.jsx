import { toneFor } from "../../config/badgeTones.js";

export default function StatusBadge({ value, badgeKind }) {
  if (value === null || value === undefined || value === "") return <span className="text-muted">—</span>;
  const tone = toneFor(badgeKind, value);
  return <span className={`badge badge-${tone}`}>{String(value)}</span>;
}
