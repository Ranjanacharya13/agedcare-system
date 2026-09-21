import { Routes, Route, useLocation } from "react-router-dom";
import AppShell from "./components/layout/AppShell.jsx";
import { DirectoryProvider } from "./context/DirectoryContext.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import RequireAuth from "./components/auth/RequireAuth.jsx";
import RequireRole from "./components/auth/RequireRole.jsx";
import ErrorBoundary from "./components/common/ErrorBoundary.jsx";
import PublicLandingPage from "./pages/PublicLandingPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ResidentsListPage from "./pages/ResidentsListPage.jsx";
import ResidentDetailPage from "./pages/ResidentDetailPage.jsx";
import EmployeesListPage from "./pages/EmployeesListPage.jsx";
import EmployeeDetailPage from "./pages/EmployeeDetailPage.jsx";
import ComplaintsPage from "./pages/ComplaintsPage.jsx";
import AppointmentsPage from "./pages/AppointmentsPage.jsx";
import AuditLogPage from "./pages/AuditLogPage.jsx";
import CoveragePage from "./pages/CoveragePage.jsx";
import UsersPage from "./pages/UsersPage.jsx";
import AccountPage from "./pages/AccountPage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";

export default function App() {
  const location = useLocation();

  return (
    <AuthProvider>
      {/* Keyed on the path so a screen that throws recovers when the user
          navigates away, instead of staying broken until a page reload. */}
      <ErrorBoundary resetKey={location.pathname}>
        <Routes>
          <Route path="/" element={<PublicLandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/admin"
            element={
              <RequireAuth>
                <DirectoryProvider>
                  <AppShell />
                </DirectoryProvider>
              </RequireAuth>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="account" element={<AccountPage />} />
            <Route
              path="residents"
              element={
                <RequireRole group="residents">
                  <ResidentsListPage />
                </RequireRole>
              }
            />
            <Route
              path="residents/:residentId/:tab?"
              element={
                <RequireRole group="residents">
                  <ResidentDetailPage />
                </RequireRole>
              }
            />
            <Route
              path="employees"
              element={
                <RequireRole group="employees">
                  <EmployeesListPage />
                </RequireRole>
              }
            />
            <Route
              path="employees/:employeeId/:tab?"
              element={
                <RequireRole group="employees">
                  <EmployeeDetailPage />
                </RequireRole>
              }
            />
            <Route
              path="complaints"
              element={
                <RequireRole group="complaints">
                  <ComplaintsPage />
                </RequireRole>
              }
            />
            <Route
              path="appointments"
              element={
                <RequireRole group="appointments">
                  <AppointmentsPage />
                </RequireRole>
              }
            />
            <Route
              path="coverage"
              element={
                <RequireRole group="assignments">
                  <CoveragePage />
                </RequireRole>
              }
            />
            <Route
              path="audit-log"
              element={
                <RequireRole group="audit">
                  <AuditLogPage />
                </RequireRole>
              }
            />
            <Route
              path="users"
              element={
                <RequireRole group="users">
                  <UsersPage />
                </RequireRole>
              }
            />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </ErrorBoundary>
    </AuthProvider>
  );
}
