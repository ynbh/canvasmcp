
import { tool } from "ai";
import { getOutcomeResultsDataSchema } from "./aitm.schema.ts";
import { getOutcomeResults, GetOutcomeResultsData } from "..";

export default tool({
  description: `
  Get outcome results
Gets the outcome results for users and outcomes in the specified context.
    `,
  parameters: getOutcomeResultsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetOutcomeResultsData, "url"> ) => {
    try {
      const { data } = await getOutcomeResults(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    