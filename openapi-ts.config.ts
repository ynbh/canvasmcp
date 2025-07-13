import type { CreateClientConfig } from "@hey-api/client-fetch";

export const createClientConfig: CreateClientConfig = (config) => ({
  ...config,
  auth: () => `${process.env.CANVAS_API_TOKEN ?? ""}`,
  baseURL: "https://canvas.instructure.com/api"
});