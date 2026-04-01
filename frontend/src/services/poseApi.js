import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });

export const detectPose = (formData) =>
  api.post("/api/v1/pose", formData, { headers: { "Content-Type": "multipart/form-data" } });
