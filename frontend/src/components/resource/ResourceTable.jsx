import Table from "../common/Table.jsx";
import Button from "../common/Button.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import { useDirectory } from "../../hooks/useDirectory.js";
import { personLabel } from "../../hooks/useDirectory.js";
import {
  formatDate,
  formatDateTime,
  formatTime,
  formatBoolean,
  formatNumber,
} from "../../utils/format.js";

function renderCell(field, row, residentsById, employeesById) {
  const value = row[field.name];
  switch (field.type) {
    case "enum":
      return <StatusBadge value={value} badgeKind={field.badgeKind} />;
    case "boolean":
      return field.badgeKind ? (
        <StatusBadge value={value ? "true" : "false"} badgeKind={field.badgeKind} />
      ) : (
        formatBoolean(value)
      );
    case "date":
      return formatDate(value);
    case "datetime":
      return formatDateTime(value);
    case "time":
      return formatTime(value);
    case "number":
      return formatNumber(value);
    case "reference": {
      if (!value) return "—";
      if (field.reference.scope === "global") {
        const source = field.reference.resource === "residents" ? residentsById : employeesById;
        const person = source[value];
        return person ? personLabel(person, field.reference.labelFields) : value.slice(0, 8);
      }
      return value.slice(0, 8);
    }
    default:
      return value ?? "—";
  }
}

export default function ResourceTable({ resource, items, onEdit, onDelete, onRowClick, extraRowActions }) {
  const { residentsById, employeesById } = useDirectory();

  const visibleFields = resource.fields.filter((f) => f.type !== "group" && f.showInTable !== false);

  const columns = [
    ...visibleFields.map((field) => ({
      key: field.name,
      label: field.label,
      render: (row) => renderCell(field, row, residentsById, employeesById),
    })),
    ...(resource.timestampField
      ? [
          {
            key: resource.timestampField,
            label: "Recorded",
            render: (row) => formatDateTime(row[resource.timestampField]),
          },
        ]
      : []),
    {
      key: "__actions",
      label: "",
      render: (row) => (
        <div className="row-actions" onClick={(e) => e.stopPropagation()}>
          {extraRowActions && extraRowActions(row)}
          <Button variant="secondary" size="sm" onClick={() => onEdit(row)}>
            Edit
          </Button>
          <Button variant="danger" size="sm" onClick={() => onDelete(row)}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      rows={items}
      onRowClick={onRowClick}
      emptyMessage={`No ${resource.label.toLowerCase()} records yet.`}
    />
  );
}
