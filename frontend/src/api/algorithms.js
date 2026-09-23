import { get, post } from "./client.js";

/** Ranked carers for one resident, while adding a single assignment (SAW + lexicographic ranking). */
export const getSuggestedCarers = (residentId, [dayStart, dayEnd], options) =>
  get(
    `/residents/${residentId}/suggested-carers?limit=5&day_start=${encodeURIComponent(dayStart.toISOString())}&day_end=${encodeURIComponent(dayEnd.toISOString())}`,
    options
  );

/** A proposed primary carer for every resident missing one (SAW + lexicographic ranking). */
export const suggestAssignments = (options) =>
  post("/coverage/suggest-assignments", undefined, options);

/** SAW-based roster recommendation for shifts (SAW score + lexicographic ranking). */
export const optimiseRoster = (body = {}, options) =>
  post("/roster/optimise", { max_candidates: 200, ...body }, options);

/** Single resident's clinical risk score and 5-factor SAW breakdown. */
export const getResidentRiskScore = (residentId, options) =>
  get(`/residents/${residentId}/risk-score`, options);

/** The Australian clinical SAW weights model. */
export const getRiskWeights = (options) =>
  get("/risk-weights", options);
