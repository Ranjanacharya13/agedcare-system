import { useState } from "react";
import { useApiResource } from "../../hooks/useApiResource.js";
import ResourceTable from "./ResourceTable.jsx";
import ResourceForm from "./ResourceForm.jsx";
import Modal from "../common/Modal.jsx";
import Button from "../common/Button.jsx";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

export default function ResourcePanel({ resource, parentId, extraRowActions, onRowClick, hideAdd }) {
  const { items, loading, error, create, update, remove } = useApiResource(resource, parentId);
  const [editingRecord, setEditingRecord] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const openCreate = () => {
    setEditingRecord(null);
    setShowForm(true);
  };
  const openEdit = (record) => {
    setEditingRecord(record);
    setShowForm(true);
  };
  const closeForm = () => setShowForm(false);

  const handleSubmit = async (values) => {
    if (editingRecord) {
      await update(editingRecord.id, values);
    } else {
      await create(values);
    }
    setShowForm(false);
  };

  const confirmDelete = async () => {
    await remove(deleteTarget.id);
    setDeleteTarget(null);
  };

  return (
    <div className="resource-panel fade-slide-in">
      <div className="resource-panel-header">
        {!hideAdd && (
          <Button variant="primary" size="sm" onClick={openCreate}>
            + Add {resource.label}
          </Button>
        )}
      </div>

      <ErrorBanner error={error} />

      {loading ? (
        <Skeleton rows={3} />
      ) : (
        <ResourceTable
          resource={resource}
          items={items}
          onEdit={openEdit}
          onDelete={setDeleteTarget}
          onRowClick={onRowClick}
          extraRowActions={extraRowActions}
        />
      )}

      {showForm && (
        <Modal title={`${editingRecord ? "Edit" : "Add"} ${resource.label}`} onClose={closeForm}>
          <ResourceForm
            resource={resource}
            record={editingRecord}
            parentId={parentId}
            onSubmit={handleSubmit}
            onCancel={closeForm}
          />
        </Modal>
      )}

      {deleteTarget && (
        <Modal
          title={`Delete ${resource.label}?`}
          onClose={() => setDeleteTarget(null)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={confirmDelete}>
                Delete
              </Button>
            </>
          }
        >
          <p>This can't be undone.</p>
        </Modal>
      )}
    </div>
  );
}
