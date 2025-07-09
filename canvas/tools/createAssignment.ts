
import { tool } from "ai";
import { createAssignmentDataSchema } from "./aitm.schema.ts";
import { createAssignment, CreateAssignmentData } from "..";

export default tool({
  description: `
  Create an assignment
Create a new assignment for this course. The assignment is created in
the
active state.
    `,
  parameters: createAssignmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateAssignmentData, "url"> ) => {
    try {
      const { data } = await createAssignment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    