export function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString();
}

export function formatDateTime(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export function formatTime(value) {
  if (!value) return "—";
  return value.slice(0, 5);
}

export function formatBoolean(value) {
  if (value === null || value === undefined) return "—";
  return value ? "Yes" : "No";
}

export function formatNumber(value) {
  if (value === null || value === undefined) return "—";
  return String(value);
}

/** Today's (or any date's) YYYY-MM-DD in the browser's own timezone — never UTC via toISOString. */
export function localDateString(date = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function initials(firstName, lastName) {
  return `${(firstName || "?")[0]}${(lastName || "")[0] || ""}`.toUpperCase();
}

export function formatRelativeDay(value) {
  if (!value) return "—";
  const date = new Date(value);
  const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const diffDays = Math.round((startOfDay(date) - startOfDay(new Date())) / 86400000);
  const time = date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  if (diffDays === 0) return `Today, ${time}`;
  if (diffDays === 1) return `Tomorrow, ${time}`;
  return date.toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function toDatetimeInputValue(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
}
