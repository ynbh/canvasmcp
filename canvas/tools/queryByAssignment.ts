
import { tool } from "ai";
import { queryByAssignmentDataSchema } from "./aitm.schema.ts";
import { queryByAssignment, QueryByAssignmentData } from "..";

export default tool({
  description: `
  Query by assignment.
List grade change events for a given assignment.
    `,
  parameters: queryByAssignmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByAssignmentData, "url"> ) => {
    try {
      const { data } = await queryByAssignment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    