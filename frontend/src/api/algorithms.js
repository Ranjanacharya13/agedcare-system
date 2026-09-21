import { get, post } from "./client.js";

/** Ranked carers for one resident, while adding a single assignment. */
export const getSuggestedCarers = (residentId, options) =>
  get(`/residents/${residentId}/suggested-carers?limit=5`, options);

/** A proposed primary carer for every resident missing one (SAW + lexicographic ranking). */
export const suggestAssignments = (options) =>
  post("/coverage/suggest-assignments", undefined, options);

/** SAW-based roster recommendation for shifts (SAW score + lexicographic ranking). */
export const optimiseRoster = (body = {}, options) =>
  post("/roster/optimise", { max_candidates: 200, ...body }, options);
