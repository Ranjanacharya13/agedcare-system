export default function Tabs({ tabs, activeKey, onChange }) {
  return (
    <div className="tabs">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`tab-btn ${activeKey === tab.key ? "tab-btn-active" : ""}`}
          onClick={() => onChange(tab.key)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
