import { Link } from "react-router-dom";
import { IconKangaroo } from "../components/layout/Icons.jsx";

// Reused both as the top-level catch-all (no AppShell around it) and as the
// nested /admin/* catch-all (already inside AppShell's sidebar+content
// layout) -- stays a plain in-flow `.page` block so it doesn't fight either
// container.
export default function NotFoundPage() {
  return (
    <div className="page not-found-page fade-slide-in">
      <IconKangaroo size={72} className="not-found-mascot" />
      <h1 className="page-title">Page not found</h1>
      <p className="text-muted">Looks like this page hopped off somewhere else.</p>
      <Link to="/admin" className="btn btn-primary btn-md">
        Back to Dashboard
      </Link>
    </div>
  );
}
