import { apiClient } from "./client";

export async function listPartners() {
  return apiClient.get("/partners");
}

export async function createPartner(payload: unknown) {
  return apiClient.post("/partners", payload);
}

export async function getPartner(partnerId: string) {
  return apiClient.get(`/partners/${partnerId}`);
}

export async function updatePartner(partnerId: string, payload: unknown) {
  return apiClient.put(`/partners/${partnerId}`, payload);
}

export async function deletePartner(partnerId: string) {
  return apiClient.delete(`/partners/${partnerId}`);
}
