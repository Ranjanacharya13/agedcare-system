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

export function initials(firstName, lastName) {
  return `${(firstName || "?")[0]}${(lastName || "")[0] || ""}`.toUpperCase();
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
