import { Routes, Route } from "react-router-dom";
import AppShell from "./components/layout/AppShell.jsx";
import { DirectoryProvider } from "./context/DirectoryContext.jsx";
import PublicLandingPage from "./pages/PublicLandingPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ResidentsListPage from "./pages/ResidentsListPage.jsx";
import ResidentDetailPage from "./pages/ResidentDetailPage.jsx";
import EmployeesListPage from "./pages/EmployeesListPage.jsx";
import EmployeeDetailPage from "./pages/EmployeeDetailPage.jsx";
import ComplaintsPage from "./pages/ComplaintsPage.jsx";
import AppointmentsPage from "./pages/AppointmentsPage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PublicLandingPage />} />
      <Route
        path="/admin"
        element={
          <DirectoryProvider>
            <AppShell />
          </DirectoryProvider>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="residents" element={<ResidentsListPage />} />
        <Route path="residents/:residentId/:tab?" element={<ResidentDetailPage />} />
        <Route path="employees" element={<EmployeesListPage />} />
        <Route path="employees/:employeeId/:tab?" element={<EmployeeDetailPage />} />
        <Route path="complaints" element={<ComplaintsPage />} />
        <Route path="appointments" element={<AppointmentsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
