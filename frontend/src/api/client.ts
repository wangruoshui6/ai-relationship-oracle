import axios from "axios";

export const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("ai-relationship-oracle-token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
