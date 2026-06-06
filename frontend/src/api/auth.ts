import { apiClient } from "./client";

export async function register(email: string, password: string) {
  return apiClient.post("/auth/register", { email, password });
}

export async function login(email: string, password: string) {
  return apiClient.post("/auth/login", { email, password });
}
