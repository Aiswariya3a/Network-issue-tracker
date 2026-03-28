import axios from "axios";
import { clearAuthToken, getAuthToken } from "../utils/auth";

const PRODUCTION_API_BASE_URL = "https://network-issue-tracker-d2dj.onrender.com";
const defaultApiBaseUrl = import.meta.env.DEV ? "/api" : PRODUCTION_API_BASE_URL;

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || defaultApiBaseUrl,
  timeout: 15000
});

api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error:", error?.response || error);
    if (error.response?.status === 401) {
      clearAuthToken();
    }
    return Promise.reject(error);
  }
);

export async function fetchIssues() {
  const { data } = await api.get("/issues");
  return data;
}

export async function fetchDashboard() {
  const { data } = await api.get("/dashboard");
  return data;
}

export async function login(payload) {
  const { data } = await api.post("/login", payload);
  return data;
}

export async function updateIssueStatus(rowIndex, status, resolutionNote = "") {
  const { data } = await api.put(`/update-status/${rowIndex}`, {
    status,
    resolution_note: resolutionNote
  });
  return data;
}
