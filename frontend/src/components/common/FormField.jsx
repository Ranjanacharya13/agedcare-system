import ReferenceSelect from "./ReferenceSelect.jsx";
import { toDatetimeInputValue } from "../../utils/format.js";

export default function FormField({ field, value, onChange, parentId }) {
  const id = `field-${field.name}`;

  if (field.type === "group") {
    const groupValue = value || {};
    return (
      <fieldset className="form-group-fieldset">
        <legend>{field.label}</legend>
        {field.fields.map((sub) => (
          <FormField
            key={sub.name}
            field={sub}
            value={groupValue[sub.name]}
            onChange={(v) => onChange({ ...groupValue, [sub.name]: v })}
            parentId={parentId}
          />
        ))}
      </fieldset>
    );
  }

  return (
    <label className="form-field" htmlFor={id}>
      <span className="form-field-label">
        {field.label}
        {field.required && <span className="required-mark">*</span>}
      </span>
      {renderInput(field, id, value, onChange, parentId)}
    </label>
  );
}

function renderInput(field, id, value, onChange, parentId) {
  switch (field.type) {
    case "textarea":
      return (
        <textarea
          id={id}
          className="input-textarea"
          value={value ?? ""}
          required={field.required}
          onChange={(e) => onChange(e.target.value)}
        />
      );
    case "number":
      return (
        <input
          id={id}
          type="number"
          className="input-text"
          value={value ?? ""}
          required={field.required}
          onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))}
        />
      );
    case "boolean":
      return (
        <input
          id={id}
          type="checkbox"
          className="input-checkbox"
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
        />
      );
    case "date":
      return (
        <input
          id={id}
          type="date"
          className="input-text"
          value={value ?? ""}
          required={field.required}
          onChange={(e) => onChange(e.target.value || null)}
        />
      );
    case "time":
      return (
        <input
          id={id}
          type="time"
          className="input-text"
          value={value ?? ""}
          required={field.required}
          onChange={(e) => onChange(e.target.value || null)}
        />
      );
    case "datetime":
      return (
        <input
          id={id}
          type="datetime-local"
          className="input-text"
          value={toDatetimeInputValue(value)}
          required={field.required}
          onChange={(e) => onChange(e.target.value ? new Date(e.target.value).toISOString() : null)}
        />
      );
    case "enum":
      return (
        <select
          id={id}
          className="input-select"
          value={value ?? ""}
          required={field.required}
          onChange={(e) => onChange(e.target.value || null)}
        >
          <option value="">— Select —</option>
          {field.options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      );
    case "reference":
      return <ReferenceSelect field={field} value={value} onChange={onChange} parentId={parentId} />;
    default:
      return (
        <input
          id={id}
          type="text"
          className="input-text"
          value={value ?? ""}
          required={field.required}
          onChange={(e) => onChange(e.target.value)}
        />
      );
  }
}
