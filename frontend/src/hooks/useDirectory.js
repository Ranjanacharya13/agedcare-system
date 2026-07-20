import { useDirectoryContext } from "../context/DirectoryContext.jsx";

export function useDirectory() {
  return useDirectoryContext();
}

export function personLabel(person, labelFields = ["first_name", "last_name"]) {
  if (!person) return null;
  return labelFields.map((f) => person[f]).filter(Boolean).join(" ");
}
