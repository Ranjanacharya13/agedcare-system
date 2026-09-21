import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
  UNAUTHORIZED_EVENT,
  authEvents,
  getToken,
  setToken,
} from "../api/client.js";
import { fetchCurrentUser, login as loginRequest } from "../api/auth.js";
import { can } from "../config/permissions.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState(getToken() ? "checking" : "anonymous");

  const signOut = useCallback(() => {
    setToken(null);
    setUser(null);
    setStatus("anonymous");
  }, []);

  useEffect(() => {
    if (!getToken()) return undefined;

    const controller = new AbortController();
    fetchCurrentUser({ signal: controller.signal })
      .then((me) => {
        setUser(me);
        setStatus("authenticated");
      })
      .catch(() => {
        setToken(null);
        setUser(null);
        setStatus("anonymous");
      });

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const handler = () => signOut();
    authEvents.addEventListener(UNAUTHORIZED_EVENT, handler);
    return () => authEvents.removeEventListener(UNAUTHORIZED_EVENT, handler);
  }, [signOut]);

  const login = useCallback(async (email, password) => {
    const response = await loginRequest(email, password);
    setToken(response.access_token);
    setUser(response.user);
    setStatus("authenticated");
    return response.user;
  }, []);

  const value = useMemo(
    () => ({
      user,
      status,
      isAuthenticated: status === "authenticated",
      isChecking: status === "checking",
      role: user?.access_role ?? null,
      displayName: user?.full_name || user?.email || "Staff",
      login,
      logout: signOut,
      /** Ask before rendering: `can("employee_hr", "read")`. */
      can: (group, action = "read") => can(user?.access_role, group, action),
    }),
    [user, status, login, signOut]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
