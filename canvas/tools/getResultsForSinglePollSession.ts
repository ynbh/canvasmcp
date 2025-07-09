
import { tool } from "ai";
import { getResultsForSinglePollSessionDataSchema } from "./aitm.schema.ts";
import { getResultsForSinglePollSession, GetResultsForSinglePollSessionData } from "..";

export default tool({
  description: `
  Get the results for a single poll session
Returns the poll session with the given id
    `,
  parameters: getResultsForSinglePollSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetResultsForSinglePollSessionData, "url"> ) => {
    try {
      const { data } = await getResultsForSinglePollSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    