
import { tool } from "ai";
import { activityStreamSummaryDataSchema } from "./aitm.schema.ts";
import { activityStreamSummary, ActivityStreamSummaryData } from "..";

export default tool({
  description: `
  Activity stream summary
Returns a summary of the current user's global activity stream.
    `,
  parameters: activityStreamSummaryDataSchema.omit({ url: true }),
  execute: async (args : Omit<ActivityStreamSummaryData, "url"> ) => {
    try {
      const { data } = await activityStreamSummary(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    