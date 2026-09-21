import { useState } from "react";
import { useParams } from "react-router-dom";
import { useAsync } from "../hooks/useAsync.js";
import { createResourceApi } from "../api/resourceApi.js";
import { residentsConfig } from "../config/residents.config.js";
import { residentResourceConfigs } from "../config/residentResourceConfigs.js";
import ResidentHeaderCard from "../components/residents/ResidentHeaderCard.jsx";
import WorkspaceSidebar from "../components/layout/WorkspaceSidebar.jsx";
import ResidentOverview from "../components/residents/ResidentOverview.jsx";
import CareTeamPanel from "../components/residents/CareTeamPanel.jsx";
import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";
import { ageFromDob, isDisabledStatus, residentTone } from "../utils/residentTone.js";
import { initials } from "../utils/format.js";

const residentsApi = createResourceApi(residentsConfig);

const groups = [
  {
    title: "Summary",
    items: [
      { key: "overview", label: "Overview" },
      { key: "care-team", label: "Care Team" },
    ],
  },
  {
    title: "Records",
    items: residentResourceConfigs.map((c) => ({ key: c.slug, label: c.label })),
  },
];

export default function ResidentDetailPage() {
  const { residentId, tab } = useParams();
  const activeTab = tab || "overview";

  const { data: fetchedResident, loading, error } = useAsync(
    () => residentsApi.getOne(residentId),
    [residentId]
  );
  const [resident, setResident] = useState(null);
  const current = resident || fetchedResident;

  if (loading && !current) return <Skeleton rows={5} />;
  if (error) return <ErrorBanner error={error} />;
  if (!current) return null;

  const activeConfig = residentResourceConfigs.find((c) => c.slug === activeTab);
  const baseUrl = `/admin/residents/${residentId}`;

  return (
    <div className={`resident-workspace tone-${residentTone(current.cognitive_status)}`}>
      <WorkspaceSidebar
        tone={residentTone(current.cognitive_status)}
        backTo="/admin/residents"
        backLabel="All residents"
        avatar={initials(current.first_name, current.last_name)}
        title={`${current.first_name} ${current.last_name}`}
        subtitle={`Room ${current.room_number || "—"}${ageFromDob(current.dob) !== null ? ` · ${ageFromDob(current.dob)} yrs` : ""}`}
        pill={`${current.cognitive_status || "Not classified"}${isDisabledStatus(current.cognitive_status) ? " · Disability" : ""}`}
        groups={groups}
        baseUrl={baseUrl}
        activeKey={activeTab}
      />
      <div className="resident-workspace-main page">
        <ResidentHeaderCard resident={current} onUpdated={setResident} />
        <div className="tab-panel">
          {activeTab === "overview" && <ResidentOverview resident={current} baseUrl={baseUrl} />}
          {activeTab === "care-team" && <CareTeamPanel residentId={residentId} />}
          {activeConfig && (
            <ResourcePanel key={activeConfig.slug} resource={activeConfig} parentId={residentId} />
          )}
        </div>
      </div>
    </div>
  );
}
