import { get } from "./client.js";

export const getHealth = () => get("/health");
