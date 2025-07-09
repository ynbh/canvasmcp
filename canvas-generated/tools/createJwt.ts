
import { tool } from "ai";
import { createJwtDataSchema } from "./aitm.schema.ts";
import { createJwt, CreateJwtData } from "..";

export default tool({
  description: `
  Create JWT
Create a unique jwt for using with other canvas services

Generates a different JWT each
time it's called, each one expires
after a short window (1 hour)
    `,
  parameters: createJwtDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateJwtData, "url"> ) => {
    try {
      const { data } = await createJwt(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    