export default function Skeleton({ rows = 3 }) {
  return (
    <div className="skeleton-block">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton-line" style={{ animationDelay: `${i * 60}ms` }} />
      ))}
    </div>
  );
}
