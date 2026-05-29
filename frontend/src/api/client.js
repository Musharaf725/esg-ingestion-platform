import axios from "axios";
import { getStoredTenant } from "../hooks/useTenant";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const tenant = getStoredTenant();
  if (tenant) {
    config.headers["X-Tenant"] = tenant;
  }
  return config;
});

export default api;
