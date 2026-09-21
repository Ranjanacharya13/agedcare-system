export function residentTone(status) {
  const nonCognitive = typeof status === "string" && status.includes("Non-Cognitive");
  return nonCognitive ? "non-cognitive" : "cognitive";
}

export function isDisabledStatus(status) {
  return typeof status === "string" && status.startsWith("Disabled");
}

export function ageFromDob(dob) {
  if (!dob) return null;
  const born = new Date(dob);
  if (Number.isNaN(born.getTime())) return null;
  const now = new Date();
  let age = now.getFullYear() - born.getFullYear();
  const hadBirthday =
    now.getMonth() > born.getMonth() ||
    (now.getMonth() === born.getMonth() && now.getDate() >= born.getDate());
  if (!hadBirthday) age -= 1;
  return age;
}
