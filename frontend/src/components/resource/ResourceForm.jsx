import { useState } from "react";
import FormField from "../common/FormField.jsx";
import Button from "../common/Button.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

function defaultForField(field) {
  if (field.type === "group") {
    return Object.fromEntries(field.fields.map((sub) => [sub.name, defaultForField(sub)]));
  }
  if (field.defaultValue !== undefined) return field.defaultValue;
  if (field.type === "boolean") return false;
  return null;
}

function isVisible(field, mode) {
  if (field.readOnly) return false;
  if (mode === "create") return !field.editOnly;
  return !field.createOnly;
}

function buildInitialValues(fields, record, mode) {
  const values = {};
  for (const field of fields) {
    if (!isVisible(field, mode)) continue;
    values[field.name] = record ? record[field.name] : defaultForField(field);
  }
  return values;
}

export default function ResourceForm({ resource, record, parentId, onSubmit, onCancel }) {
  const mode = record ? "edit" : "create";
  const [values, setValues] = useState(() => buildInitialValues(resource.fields, record, mode));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const visibleFields = resource.fields.filter((f) => isVisible(f, mode));

  const handleChange = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSubmit(values);
    } catch (err) {
      setError(err);
      setSaving(false);
    }
  };

  return (
    <form className="resource-form" onSubmit={handleSubmit}>
      <ErrorBanner error={error} />
      {visibleFields.map((field) => (
        <FormField
          key={field.name}
          field={field}
          value={values[field.name]}
          onChange={(v) => handleChange(field.name, v)}
          parentId={parentId}
        />
      ))}
      <div className="resource-form-actions">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" disabled={saving}>
          {saving ? "Saving…" : mode === "create" ? "Create" : "Save changes"}
        </Button>
      </div>
    </form>
  );
}
