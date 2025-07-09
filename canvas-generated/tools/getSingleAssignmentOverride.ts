
import { tool } from "ai";
import { getSingleAssignmentOverrideDataSchema } from "./aitm.schema.ts";
import { getSingleAssignmentOverride, GetSingleAssignmentOverrideData } from "..";

export default tool({
  description: `
  Get a single assignment override
Returns details of the the override with the given id.
    `,
  parameters: getSingleAssignmentOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleAssignmentOverrideData, "url"> ) => {
    try {
      const { data } = await getSingleAssignmentOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    