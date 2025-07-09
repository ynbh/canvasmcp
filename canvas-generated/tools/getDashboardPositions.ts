
import { tool } from "ai";
import { getDashboardPositionsDataSchema } from "./aitm.schema.ts";
import { getDashboardPositions, GetDashboardPositionsData } from "..";

export default tool({
  description: `
  Get dashboard positions
Returns all dashboard positions that have been saved for a user.
    `,
  parameters: getDashboardPositionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetDashboardPositionsData, "url"> ) => {
    try {
      const { data } = await getDashboardPositions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    