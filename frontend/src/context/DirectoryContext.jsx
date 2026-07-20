import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { get } from "../api/client.js";

const DirectoryContext = createContext(null);

// No search endpoint exists on the backend and facility rosters are small,
// so loading the full residents+employees lists once (up to 1000 rows each)
// is the affordable strategy for name lookups and reference dropdowns
// everywhere in the app.
export function DirectoryProvider({ children }) {
  const [residents, setResidents] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([get("/residents?skip=0&limit=1000"), get("/employees?skip=0&limit=1000")])
      .then(([residentsData, employeesData]) => {
        if (cancelled) return;
        setResidents(residentsData);
        setEmployees(employeesData);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const residentsById = useMemo(
    () => Object.fromEntries(residents.map((r) => [r.id, r])),
    [residents]
  );
  const employeesById = useMemo(
    () => Object.fromEntries(employees.map((e) => [e.id, e])),
    [employees]
  );

  const value = useMemo(
    () => ({
      residents,
      employees,
      residentsById,
      employeesById,
      loading,
      refresh: () => setRefreshKey((k) => k + 1),
    }),
    [residents, employees, residentsById, employeesById, loading]
  );

  return <DirectoryContext.Provider value={value}>{children}</DirectoryContext.Provider>;
}

export function useDirectoryContext() {
  const ctx = useContext(DirectoryContext);
  if (!ctx) throw new Error("useDirectoryContext must be used within a DirectoryProvider");
  return ctx;
}
