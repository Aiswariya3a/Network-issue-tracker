const TOKEN_KEY = "nims_token";
export const AUTH_LOGOUT_EVENT = "auth:logout";
const COORDINATOR_ROLES = new Set(["ICT", "Infra"]);

export function setAuthToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearAuthToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated() {
  const token = getAuthToken();
  if (!token) {
    return false;
  }

  const payload = parseJwtPayload(token);
  if (!payload || isTokenExpired(payload)) {
    return false;
  }

  return true;
}

function parseJwtPayload(token) {
  try {
    const [, payloadPart] = token.split(".");
    if (!payloadPart) {
      return null;
    }
    const normalized = payloadPart.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
    return JSON.parse(window.atob(padded));
  } catch {
    return null;
  }
}

function isTokenExpired(payload) {
  const exp = Number(payload?.exp);
  if (!Number.isFinite(exp)) {
    return true;
  }
  const nowInSeconds = Math.floor(Date.now() / 1000);
  return exp <= nowInSeconds;
}

export function getAuthFailureReason(requiredRole = false) {
  const token = getAuthToken();
  if (!token) {
    return "missing";
  }

  const payload = parseJwtPayload(token);
  if (!payload) {
    return "expired";
  }
  if (isTokenExpired(payload)) {
    return "expired";
  }

  if (requiredRole) {
    const role = String(payload.role || "");
    if (!COORDINATOR_ROLES.has(role)) {
      return "unauthorized";
    }
  }

  return null;
}

export function triggerLogoutRedirect(reason = "expired") {
  window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT, { detail: { reason } }));
}
