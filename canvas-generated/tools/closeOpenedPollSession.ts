
import { tool } from "ai";
import { closeOpenedPollSessionDataSchema } from "./aitm.schema.ts";
import { closeOpenedPollSession, CloseOpenedPollSessionData } from "..";

export default tool({
  description: `
  Close an opened poll session
    `,
  parameters: closeOpenedPollSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CloseOpenedPollSessionData, "url"> ) => {
    try {
      const { data } = await closeOpenedPollSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    