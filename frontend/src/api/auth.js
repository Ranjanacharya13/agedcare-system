import { get, patch, post, del } from "./client.js";

export const login = (email, password) => post("/auth/login", { email, password });

export const fetchCurrentUser = (options) => get("/auth/me", options);

export const changePassword = (currentPassword, newPassword) =>
  post("/auth/change-password", {
    current_password: currentPassword,
    new_password: newPassword,
  });

export const listUsers = (options) => get("/users", options);
export const createUser = (data) => post("/users", data);
export const updateUser = (id, data) => patch(`/users/${id}`, data);
export const deleteUser = (id) => del(`/users/${id}`);
export const resetUserPassword = (id, newPassword) =>
  post(`/users/${id}/reset-password`, { new_password: newPassword });

export const listAuditLog = (params = {}, options) => {
  const query = new URLSearchParams();
  if (params.skip) query.set("skip", params.skip);
  if (params.limit) query.set("limit", params.limit);
  const suffix = query.toString() ? `?${query}` : "";
  return get(`/audit-log${suffix}`, options);
};

export const listAuditLogForRecord = (tableName, recordId, options) =>
  get(`/audit-log/${tableName}/${recordId}`, options);
