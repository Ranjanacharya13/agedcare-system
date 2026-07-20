export default function Pager({ skip, limit, count, onChange }) {
  const hasPrev = skip > 0;
  const hasNext = count === limit;

  return (
    <div className="pager">
      <button className="btn btn-secondary btn-sm" disabled={!hasPrev} onClick={() => onChange(Math.max(0, skip - limit))}>
        Previous
      </button>
      <span className="text-muted pager-label">
        Showing {skip + 1}–{skip + count}
      </span>
      <button className="btn btn-secondary btn-sm" disabled={!hasNext} onClick={() => onChange(skip + limit)}>
        Next
      </button>
    </div>
  );
}
