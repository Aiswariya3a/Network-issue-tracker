const TOKEN_KEY = "nims_token";
export const AUTH_LOGOUT_EVENT = "auth:logout";

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
  return Boolean(getAuthToken());
}

export function triggerLogoutRedirect() {
  window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
}
