import { apiClient } from "./client";

export async function getMyProfile() {
  return apiClient.get("/profiles/me");
}

export async function upsertMyProfile(payload: unknown) {
  return apiClient.put("/profiles/me", payload);
}
