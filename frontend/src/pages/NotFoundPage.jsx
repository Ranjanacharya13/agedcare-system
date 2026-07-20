import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="page fade-slide-in">
      <h1 className="page-title">Page not found</h1>
      <p className="text-muted">The page you're looking for doesn't exist.</p>
      <Link to="/admin" className="btn btn-primary btn-md">
        Back to Dashboard
      </Link>
    </div>
  );
}
