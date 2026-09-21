import { useAuth } from "../../context/AuthContext.jsx";
import EmptyState from "../common/EmptyState.jsx";

export default function RequireRole({ group, action = "read", children }) {
  const { can, role } = useAuth();

  if (!can(group, action)) {
    return (
      <EmptyState
        title="You don't have access to this page"
        message={`Your role (${role ?? "unknown"}) can't view ${group.replace(/_/g, " ")}. Ask an administrator if you think this is wrong.`}
      />
    );
  }
  return children;
}

/** Inline variant for hiding a single control — a delete button, a tab. */
export function IfAllowed({ group, action = "read", children, fallback = null }) {
  const { can } = useAuth();
  return can(group, action) ? children : fallback;
}
