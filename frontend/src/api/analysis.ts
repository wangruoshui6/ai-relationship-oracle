import { apiClient } from "./client";

export async function createStructuredConsultation(payload: unknown) {
  return apiClient.post("/structured-consultations", payload);
}

export async function createConsultation(payload: unknown) {
  return apiClient.post("/consultations", payload);
}

async function streamRequest(url: string, payload: unknown, onEvent: (event: string, data: any) => void) {
  const token = localStorage.getItem("ai-relationship-oracle-token");
  const response = await fetch(`http://127.0.0.1:8000/api/v1${url}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });

  if (!response.body) {
    throw new Error("No response stream available");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    for (const part of parts) {
      const lines = part.split("\n");
      let eventName = "message";
      let dataLine = "";
      for (const line of lines) {
        if (line.startsWith("event:")) {
          eventName = line.slice(6).trim();
        }
        if (line.startsWith("data:")) {
          dataLine += line.slice(5).trim();
        }
      }
      if (dataLine) {
        onEvent(eventName, JSON.parse(dataLine));
      }
    }
  }
}

export async function streamStructuredConsultation(
  payload: unknown,
  onEvent: (event: string, data: any) => void
) {
  return streamRequest("/structured-consultations/stream", payload, onEvent);
}

export async function streamConsultation(
  payload: unknown,
  onEvent: (event: string, data: any) => void
) {
  return streamRequest("/consultations/stream", payload, onEvent);
}
