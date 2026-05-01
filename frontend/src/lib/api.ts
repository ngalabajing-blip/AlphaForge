import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/store/auth";

const api: AxiosInstance = axios.create({
  baseURL: "/_/api",
  timeout: 15000,
});

api.interceptors.request.use((cfg: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().token;
  if (token) {
    cfg.headers.Authorization = `Bearer ${token}`;
  }
  return cfg;
});

api.interceptors.response.use(
  (resp) => resp,
  (err) => {
    if (err?.response?.status === 401) {
      useAuthStore.getState().clear();
    }
    return Promise.reject(err);
  },
);

export default api;
