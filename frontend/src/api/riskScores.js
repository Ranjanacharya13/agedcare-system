import { get } from "./client.js";

export const getRiskScores = () => get("/risk-scores");
export const getResidentRiskScore = (residentId) => get(`/residents/${residentId}/risk-score`);
