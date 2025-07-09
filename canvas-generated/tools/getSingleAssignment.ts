
import { tool } from "ai";
import { getSingleAssignmentDataSchema } from "./aitm.schema.ts";
import { getSingleAssignment, GetSingleAssignmentData } from "..";

export default tool({
  description: `
  Get a single assignment
Returns the assignment with the given id.
    `,
  parameters: getSingleAssignmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleAssignmentData, "url"> ) => {
    try {
      const { data } = await getSingleAssignment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    