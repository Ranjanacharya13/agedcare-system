import { useState } from "react";
import { useParams } from "react-router-dom";
import { useAsync } from "../hooks/useAsync.js";
import { useStaffStatus } from "../hooks/useStaffStatus.js";
import { createResourceApi } from "../api/resourceApi.js";
import { employeesConfig } from "../config/employees.config.js";
import { employeeResourceConfigs, shifts as shiftsConfig } from "../config/employeeResourceConfigs.js";
import EmployeeHeaderCard from "../components/employees/EmployeeHeaderCard.jsx";
import EmployeeOverview from "../components/employees/EmployeeOverview.jsx";
import ShiftSuggestionsModal from "../components/employees/ShiftSuggestionsModal.jsx";
import CaseloadPanel from "../components/employees/CaseloadPanel.jsx";
import WorkspaceSidebar from "../components/layout/WorkspaceSidebar.jsx";
import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import Button from "../components/common/Button.jsx";
import Modal from "../components/common/Modal.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import { initials } from "../utils/format.js";

const employeesApi = createResourceApi(employeesConfig);
const shiftsApi = createResourceApi(shiftsConfig);

function isToday(dateString) {
  const d = new Date(dateString);
  const now = new Date();
  return (
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
  );
}

const groups = [
  {
    title: "Summary",
    items: [
      { key: "overview", label: "Overview" },
      { key: "caseload", label: "Assigned Residents" },
    ],
  },
  { title: "Records", items: employeeResourceConfigs.map((c) => ({ key: c.slug, label: c.label })) },
];

export default function EmployeeDetailPage() {
  const { employeeId, tab } = useParams();
  const activeTab = tab || "overview";
  const [suggestShiftId, setSuggestShiftId] = useState(null);
  const [confirmingClear, setConfirmingClear] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [shiftsKey, setShiftsKey] = useState(0);
  const { byId } = useStaffStatus();

  const { data: fetchedEmployee, loading, error } = useAsync(
    () => employeesApi.getOne(employeeId),
    [employeeId]
  );
  const [employee, setEmployee] = useState(null);
  const current = employee || fetchedEmployee;

  if (loading && !current) return <Skeleton rows={5} />;
  if (error) return <ErrorBanner error={error} />;
  if (!current) return null;

  const activeConfig = employeeResourceConfigs.find((c) => c.slug === activeTab);
  const isShiftsTab = activeTab === "shifts";
  const status = byId[employeeId];
  const tone = status?.tone || "available";
  const baseUrl = `/admin/employees/${employeeId}`;

  const handleClearTodayShifts = async () => {
    setClearing(true);
    try {
      const todaysShifts = await shiftsApi.list({ parentId: employeeId });
      const toCancel = todaysShifts.filter(
        (s) => isToday(s.shift_start) && s.status !== "Cancelled" && s.status !== "Completed"
      );
      await Promise.all(
        toCancel.map((s) => shiftsApi.update(s.id, { status: "Cancelled" }, { parentId: employeeId }))
      );
      setShiftsKey((k) => k + 1);
    } finally {
      setClearing(false);
      setConfirmingClear(false);
    }
  };

  return (
    <div className={`resident-workspace tone-${tone}`}>
      <WorkspaceSidebar
        tone={tone}
        backTo="/admin/employees"
        backLabel="All staff"
        avatar={initials(current.first_name, current.last_name)}
        title={`${current.first_name} ${current.last_name}`}
        subtitle={current.role || "Role not set"}
        pill={status?.reason || "Available"}
        groups={groups}
        baseUrl={baseUrl}
        activeKey={activeTab}
      />
      <div className="resident-workspace-main page">
        <EmployeeHeaderCard employee={current} onUpdated={setEmployee} />
        <div className="tab-panel">
          {activeTab === "overview" && (
            <EmployeeOverview employee={current} status={status} baseUrl={baseUrl} />
          )}
          {activeTab === "caseload" && <CaseloadPanel employeeId={employeeId} />}
          {isShiftsTab && (
            <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "var(--space-3)" }}>
              <Button variant="danger" size="sm" onClick={() => setConfirmingClear(true)}>
                Clear today's shifts
              </Button>
            </div>
          )}
          {activeConfig && (
            <ResourcePanel
              key={`${activeConfig.slug}-${shiftsKey}`}
              resource={activeConfig}
              parentId={employeeId}
              extraRowActions={
                isShiftsTab
                  ? (shift) => (
                      <Button variant="secondary" size="sm" onClick={() => setSuggestShiftId(shift.id)}>
                        Suggest coverage
                      </Button>
                    )
                  : undefined
              }
            />
          )}
        </div>
      </div>

      {suggestShiftId && (
        <ShiftSuggestionsModal shiftId={suggestShiftId} onClose={() => setSuggestShiftId(null)} />
      )}

      {confirmingClear && (
        <Modal
          title="Clear today's shifts?"
          onClose={() => setConfirmingClear(false)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setConfirmingClear(false)} disabled={clearing}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleClearTodayShifts} disabled={clearing}>
                {clearing ? "Clearing…" : "Clear shifts"}
              </Button>
            </>
          }
        >
          <p>This cancels every non-completed shift scheduled for today for {current.first_name} {current.last_name}. This can't be undone.</p>
        </Modal>
      )}
    </div>
  );
}
