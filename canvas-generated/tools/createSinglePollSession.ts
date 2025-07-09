
import { tool } from "ai";
import { createSinglePollSessionDataSchema } from "./aitm.schema.ts";
import { createSinglePollSession, CreateSinglePollSessionData } from "..";

export default tool({
  description: `
  Create a single poll session
Create a new poll session for this poll
    `,
  parameters: createSinglePollSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateSinglePollSessionData, "url"> ) => {
    try {
      const { data } = await createSinglePollSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    