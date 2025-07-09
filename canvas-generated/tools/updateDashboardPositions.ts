
import { tool } from "ai";
import { updateDashboardPositionsDataSchema } from "./aitm.schema.ts";
import { updateDashboardPositions, UpdateDashboardPositionsData } from "..";

export default tool({
  description: `
  Update dashboard positions
Updates the dashboard positions for a user for a given context.  This
allows
positions for the dashboard cards and elsewhere to be customized on a per
user basis.

The
asset string parameter should be in the format 'context_id', for example
'course_42'
    `,
  parameters: updateDashboardPositionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateDashboardPositionsData, "url"> ) => {
    try {
      const { data } = await updateDashboardPositions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    