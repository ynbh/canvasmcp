
import { tool } from "ai";
import { deletePlannerOverrideDataSchema } from "./aitm.schema.ts";
import { deletePlannerOverride, DeletePlannerOverrideData } from "..";

export default tool({
  description: `
  Delete a planner override
Delete a planner override for the current user
    `,
  parameters: deletePlannerOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePlannerOverrideData, "url"> ) => {
    try {
      const { data } = await deletePlannerOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    