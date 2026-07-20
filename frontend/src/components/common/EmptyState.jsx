export default function EmptyState({ title = "Nothing here yet", message, action }) {
  return (
    <div className="empty-state fade-slide-in">
      <p className="empty-state-title">{title}</p>
      {message && <p className="text-muted">{message}</p>}
      {action}
    </div>
  );
}
