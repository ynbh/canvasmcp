
import { tool } from "ai";
import { getSingleAssignmentLtiDataSchema } from "./aitm.schema.ts";
import { getSingleAssignmentLti, GetSingleAssignmentLtiData } from "..";

export default tool({
  description: `
  Get a single assignment (lti)
Get a single Canvas assignment by Canvas id or LTI id. Tool providers
may only access
assignments that are associated with their tool.
    `,
  parameters: getSingleAssignmentLtiDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleAssignmentLtiData, "url"> ) => {
    try {
      const { data } = await getSingleAssignmentLti(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    