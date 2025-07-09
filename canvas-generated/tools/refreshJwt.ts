
import { tool } from "ai";
import { refreshJwtDataSchema } from "./aitm.schema.ts";
import { refreshJwt, RefreshJwtData } from "..";

export default tool({
  description: `
  Refresh JWT
Refresh a JWT for use with other canvas services

Generates a different JWT each time
it's called, each one expires
after a short window (1 hour).
    `,
  parameters: refreshJwtDataSchema.omit({ url: true }),
  execute: async (args : Omit<RefreshJwtData, "url"> ) => {
    try {
      const { data } = await refreshJwt(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    