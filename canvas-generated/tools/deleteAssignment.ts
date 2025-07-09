
import { tool } from "ai";
import { deleteAssignmentDataSchema } from "./aitm.schema.ts";
import { deleteAssignment, DeleteAssignmentData } from "..";

export default tool({
  description: `
  Delete an assignment
Delete the given assignment.
    `,
  parameters: deleteAssignmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteAssignmentData, "url"> ) => {
    try {
      const { data } = await deleteAssignment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    