
import { tool } from "ai";
import { updateSinglePollSessionDataSchema } from "./aitm.schema.ts";
import { updateSinglePollSession, UpdateSinglePollSessionData } from "..";

export default tool({
  description: `
  Update a single poll session
Update an existing poll session for this poll
    `,
  parameters: updateSinglePollSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateSinglePollSessionData, "url"> ) => {
    try {
      const { data } = await updateSinglePollSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    