
import { tool } from "ai";
import { openPollSessionDataSchema } from "./aitm.schema.ts";
import { openPollSession, OpenPollSessionData } from "..";

export default tool({
  description: `
  Open a poll session
    `,
  parameters: openPollSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<OpenPollSessionData, "url"> ) => {
    try {
      const { data } = await openPollSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    