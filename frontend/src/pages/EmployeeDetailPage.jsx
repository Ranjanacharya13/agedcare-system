import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAsync } from "../hooks/useAsync.js";
import { createResourceApi } from "../api/resourceApi.js";
import { employeesConfig } from "../config/employees.config.js";
import { employeeResourceConfigs } from "../config/employeeResourceConfigs.js";
import EmployeeHeaderCard from "../components/employees/EmployeeHeaderCard.jsx";
import ShiftSuggestionsModal from "../components/employees/ShiftSuggestionsModal.jsx";
import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import Button from "../components/common/Button.jsx";
import Tabs from "../components/common/Tabs.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";

const employeesApi = createResourceApi(employeesConfig);

const tabs = [
  { key: "overview", label: "Overview" },
  ...employeeResourceConfigs.map((c) => ({ key: c.slug, label: c.label })),
];

export default function EmployeeDetailPage() {
  const { employeeId, tab } = useParams();
  const navigate = useNavigate();
  const activeTab = tab || "overview";
  const [suggestShiftId, setSuggestShiftId] = useState(null);

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

  return (
    <div className="page">
      <EmployeeHeaderCard employee={current} onUpdated={setEmployee} />
      <Tabs
        tabs={tabs}
        activeKey={activeTab}
        onChange={(key) =>
          navigate(
            key === "overview" ? `/admin/employees/${employeeId}` : `/admin/employees/${employeeId}/${key}`
          )
        }
      />
      <div className="tab-panel">
        {activeTab === "overview" && (
          <p className="text-muted">Select a tab above to view or manage this employee's records.</p>
        )}
        {activeConfig && (
          <ResourcePanel
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

      {suggestShiftId && (
        <ShiftSuggestionsModal shiftId={suggestShiftId} onClose={() => setSuggestShiftId(null)} />
      )}
    </div>
  );
}
