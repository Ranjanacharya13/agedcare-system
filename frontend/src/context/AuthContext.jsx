import { createContext, useCallback, useContext, useState } from "react";

const AuthContext = createContext(null);
const STORAGE_KEY = "careos_auth";

// Dummy client-side gate only -- CLAUDE.md notes there is no real auth
// anywhere in this stack yet (backend/config/security.py is unwired
// scaffolding). This just keeps /admin from being a bare URL with nothing
// in front of it; it is not a security boundary.
const DUMMY_USERNAME = "admin";
const DUMMY_PASSWORD = "careos123";

function readStoredUser() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser);

  const login = useCallback((username, password) => {
    if (
      username.trim().toLowerCase() === DUMMY_USERNAME &&
      password === DUMMY_PASSWORD
    ) {
      const nextUser = { name: "Admin" };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser));
      setUser(nextUser);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: Boolean(user), login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
