
import { tool } from "ai";
import { showPlannerOverrideDataSchema } from "./aitm.schema.ts";
import { showPlannerOverride, ShowPlannerOverrideData } from "..";

export default tool({
  description: `
  Show a planner override
Retrieve a planner override for the current user
    `,
  parameters: showPlannerOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowPlannerOverrideData, "url"> ) => {
    try {
      const { data } = await showPlannerOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    