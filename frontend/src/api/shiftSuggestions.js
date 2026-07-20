import { get } from "./client.js";

export const getSuggestedEmployees = (shiftId) => get(`/shifts/${shiftId}/suggested-employees`);
