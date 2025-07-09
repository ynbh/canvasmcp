
import { tool } from "ai";
import { createPlannerOverrideDataSchema } from "./aitm.schema.ts";
import { createPlannerOverride, CreatePlannerOverrideData } from "..";

export default tool({
  description: `
  Create a planner override
Create a planner override for the current user
    `,
  parameters: createPlannerOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreatePlannerOverrideData, "url"> ) => {
    try {
      const { data } = await createPlannerOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    