// frontend/src/services/api.js
import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:8000/api",
});

export function runWorkflow() {
  return client.get("/workflow/run");
}

export function fetchLlm(sessionId) {
  return client.get(`/workflow/llm/${sessionId}`);
}
