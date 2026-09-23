import { useMemo, useState } from "react";
import { useDirectory } from "../../hooks/useDirectory.js";
import { useAsync } from "../../hooks/useAsync.js";
import { createResourceApi } from "../../api/resourceApi.js";
import { formatDateTime } from "../../utils/format.js";

function optionLabel(item, labelFields) {
  return labelFields
    .map((field) => {
      const value = item[field];
      if (typeof value === "string" && value.includes("T")) return formatDateTime(value);
      return value;
    })
    .filter(Boolean)
    .join(" ")
    .trim() || item.id;
}

export default function ReferenceSelect({ field, value, onChange, parentId }) {
  const { resource, scope, labelFields } = field.reference;
  const [query, setQuery] = useState("");
  const { residents, employees } = useDirectory();

  const parentScopedApi = useMemo(
    () => (scope === "parent" ? createResourceApi({ slug: resource, parent: { resource: "employees" } }) : null),
    [scope, resource]
  );

  const { data: parentScopedItems } = useAsync(
    () => (scope === "parent" ? parentScopedApi.list({ parentId }) : Promise.resolve([])),
    [scope, parentId]
  );

  const all = scope === "parent" ? parentScopedItems || [] : resource === "residents" ? residents : employees;
  const items = field.reference.filter ? all.filter(field.reference.filter) : all;

  const options = useMemo(() => {
    const withLabels = items.map((item) => ({ id: item.id, label: optionLabel(item, labelFields) }));
    if (!query.trim()) return withLabels;
    const q = query.toLowerCase();
    return withLabels.filter((o) => o.label.toLowerCase().includes(q));
  }, [items, labelFields, query]);

  return (
    <div className="reference-select">
      <input
        type="text"
        className="input-text reference-filter"
        placeholder="Filter…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <select className="input-select" value={value || ""} onChange={(e) => onChange(e.target.value || null)}>
        <option value="">— None —</option>
        {options.map((opt) => (
          <option key={opt.id} value={opt.id}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
