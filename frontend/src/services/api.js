import axios from "axios";

const API_BASE = "http://localhost:8000/api";

export async function runWorkflow() {
  return axios.get(`${API_BASE}/workflow/run`);
}
