
import { tool } from "ai";
import { updatePlannerOverrideDataSchema } from "./aitm.schema.ts";
import { updatePlannerOverride, UpdatePlannerOverrideData } from "..";

export default tool({
  description: `
  Update a planner override
Update a planner override's visibilty for the current user
    `,
  parameters: updatePlannerOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdatePlannerOverrideData, "url"> ) => {
    try {
      const { data } = await updatePlannerOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    