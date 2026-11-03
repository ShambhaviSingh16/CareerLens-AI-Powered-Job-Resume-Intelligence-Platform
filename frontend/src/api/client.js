import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 90000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use((response) => response, (error) => {
  if (error.response?.status === 401 && !error.config?.url?.startsWith("/auth/login")) {
    sessionStorage.removeItem("token");
    window.location.assign("/login");
  }
  return Promise.reject(error);
});

export function errorMessage(error, fallback = "Something went wrong. Please try again.") {
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => `${item.loc?.at(-1) || "Input"}: ${item.msg || "Invalid value"}`).join(". ");
  }
  if (!error.response) return "Could not reach the server. It may be waking up; please try again shortly.";
  return fallback;
}

export default api;
