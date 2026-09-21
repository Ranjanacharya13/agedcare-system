import { Outlet, useLocation } from "react-router-dom";
import Nav from "./Nav.jsx";

const RESIDENT_WORKSPACE = /^\/admin\/(residents|employees)\/[^/]+/;

export default function AppShell() {
  const location = useLocation();
  const focused = RESIDENT_WORKSPACE.test(location.pathname);

  return (
    <div className={`app-shell${focused ? " app-shell-focused" : ""}`}>
      {!focused && <Nav />}
      <main className="app-content">
        <div key={location.pathname} className="page-transition">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
