import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAsync } from "../hooks/useAsync.js";
import { createResourceApi } from "../api/resourceApi.js";
import { residentsConfig } from "../config/residents.config.js";
import { residentResourceConfigs } from "../config/residentResourceConfigs.js";
import ResidentHeaderCard from "../components/residents/ResidentHeaderCard.jsx";
import RiskScoreCard from "../components/residents/RiskScoreCard.jsx";
import ResourcePanel from "../components/resource/ResourcePanel.jsx";
import Tabs from "../components/common/Tabs.jsx";
import Skeleton from "../components/common/Skeleton.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";

const residentsApi = createResourceApi(residentsConfig);

const tabs = [
  { key: "overview", label: "Overview" },
  { key: "risk-score", label: "Risk Score" },
  ...residentResourceConfigs.map((c) => ({ key: c.slug, label: c.label })),
];

export default function ResidentDetailPage() {
  const { residentId, tab } = useParams();
  const navigate = useNavigate();
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

  return (
    <div className="page">
      <ResidentHeaderCard resident={current} onUpdated={setResident} />
      <Tabs
        tabs={tabs}
        activeKey={activeTab}
        onChange={(key) =>
          navigate(
            key === "overview" ? `/admin/residents/${residentId}` : `/admin/residents/${residentId}/${key}`
          )
        }
      />
      <div className="tab-panel">
        {activeTab === "overview" && (
          <p className="text-muted">Select a tab above to view or manage this resident's records.</p>
        )}
        {activeTab === "risk-score" && <RiskScoreCard residentId={residentId} />}
        {activeConfig && <ResourcePanel resource={activeConfig} parentId={residentId} />}
      </div>
    </div>
  );
}
