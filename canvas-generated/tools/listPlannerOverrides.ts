
import { tool } from "ai";
import { listPlannerOverridesDataSchema } from "./aitm.schema.ts";
import { listPlannerOverrides, ListPlannerOverridesData } from "..";

export default tool({
  description: `
  List planner overrides
Retrieve a planner override for the current user
    `,
  parameters: listPlannerOverridesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPlannerOverridesData, "url"> ) => {
    try {
      const { data } = await listPlannerOverrides(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    