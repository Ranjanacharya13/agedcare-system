import { Outlet, useLocation } from "react-router-dom";
import Nav from "./Nav.jsx";

export default function AppShell() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <Nav />
      <main className="app-content">
        <div key={location.pathname} className="page-transition">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
