import { Link } from "react-router-dom";
import { IconKangaroo } from "../components/layout/Icons.jsx";

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
