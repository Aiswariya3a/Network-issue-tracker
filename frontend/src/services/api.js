import axios from "axios";
import { clearAuthToken, getAuthToken, triggerLogoutRedirect } from "../utils/auth";

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
    if ([401, 403].includes(error.response?.status)) {
      clearAuthToken();
      triggerLogoutRedirect(error.response?.status === 403 ? "unauthorized" : "expired");
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

export async function updateIssueStatus(rowIndex, { status, ictMemberName, resolutionRemark = "" }) {
  const { data } = await api.put(`/update-status/${rowIndex}`, {
    status,
    ict_member_name: ictMemberName,
    resolution_remark: resolutionRemark
  });
  return data;
}

export async function exportAdminReport(fromDate, toDate) {
  const response = await api.get("/admin/export", {
    params: {
      from_date: fromDate,
      to_date: toDate
    },
    responseType: "blob"
  });

  const disposition = response.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename="?([^"]+)"?/i);
  const filename = match?.[1] || `complaints_report_${fromDate}_to_${toDate}.xlsx`;

  return { blob: response.data, filename };
}
