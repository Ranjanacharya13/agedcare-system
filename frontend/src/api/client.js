const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const DEFAULT_TIMEOUT_MS = 15000;

const TOKEN_STORAGE_KEY = "careos_token";

export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }

  /** Field-level errors from a FastAPI 422, as {fieldName: message}.
   *  Lets a form put the message next to the input that caused it instead of
   *  showing one opaque banner at the top. */
  get fieldErrors() {
    const detail = this.body?.detail;
    if (!Array.isArray(detail)) return {};
    return detail.reduce((acc, item) => {
      // loc is like ["body", "email"]; the last entry is the field.
      const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : null;
      if (field && !acc[field]) acc[field] = item.msg;
      return acc;
    }, {});
  }
}

export class TimeoutError extends ApiError {
  constructor() {
    super("The server took too long to respond. Please try again.", 0, null);
    this.name = "TimeoutError";
  }
}

/** Raised when a request is deliberately cancelled (component unmounted, or a
 *  newer request superseded this one). Callers should swallow these — they are
 *  not failures and must never surface as an error banner. */
export class AbortedError extends Error {
  constructor() {
    super("Request aborted");
    this.name = "AbortedError";
  }
}

export function isAborted(error) {
  return error instanceof AbortedError || error?.name === "AbortError";
}

let inMemoryToken = null;

export function setToken(token) {
  inMemoryToken = token;
  try {
    if (token) localStorage.setItem(TOKEN_STORAGE_KEY, token);
    else localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch {
  }
}

export function getToken() {
  if (inMemoryToken) return inMemoryToken;
  try {
    inMemoryToken = localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    inMemoryToken = null;
  }
  return inMemoryToken;
}

export const authEvents = new EventTarget();
export const UNAUTHORIZED_EVENT = "unauthorized";

function announceUnauthorized() {
  authEvents.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
}

async function request(path, { method = "GET", body, signal, timeout = DEFAULT_TIMEOUT_MS } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(new DOMException("timeout", "TimeoutError")), timeout);

  const onExternalAbort = () => controller.abort(new DOMException("aborted", "AbortError"));
  if (signal) {
    if (signal.aborted) onExternalAbort();
    else signal.addEventListener("abort", onExternalAbort, { once: true });
  }

  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } catch (error) {
    if (controller.signal.reason?.name === "TimeoutError") throw new TimeoutError();
    if (error.name === "AbortError") throw new AbortedError();
    throw new ApiError("Could not reach the server. Check your connection.", 0, null);
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", onExternalAbort);
  }

  if (!response.ok) {
    let parsed = null;
    let detail = response.statusText;
    try {
      parsed = await response.json();
      if (typeof parsed.detail === "string") detail = parsed.detail;
      else if (Array.isArray(parsed.detail)) detail = "Please check the highlighted fields.";
    } catch {
      // Response had no JSON body.
    }

    if (response.status === 401) {
      setToken(null);
      announceUnauthorized();
    }
    throw new ApiError(detail, response.status, parsed);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const get = (path, options) => request(path, options);
export const post = (path, body, options) => request(path, { ...options, method: "POST", body });
export const patch = (path, body, options) => request(path, { ...options, method: "PATCH", body });
export const del = (path, options) => request(path, { ...options, method: "DELETE" });
