
import { tool } from "ai";
import { groupActivityStreamSummaryDataSchema } from "./aitm.schema.ts";
import { groupActivityStreamSummary, GroupActivityStreamSummaryData } from "..";

export default tool({
  description: `
  Group activity stream summary
Returns a summary of the current user's group-specific activity
stream.

For full documentation, see the API documentation for the user activity
stream summary, in
the user api.
    `,
  parameters: groupActivityStreamSummaryDataSchema.omit({ url: true }),
  execute: async (args : Omit<GroupActivityStreamSummaryData, "url"> ) => {
    try {
      const { data } = await groupActivityStreamSummary(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    