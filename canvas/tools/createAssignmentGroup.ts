
import { tool } from "ai";
import { createAssignmentGroupDataSchema } from "./aitm.schema.ts";
import { createAssignmentGroup, CreateAssignmentGroupData } from "..";

export default tool({
  description: `
  Create an Assignment Group
Create a new assignment group for this course.
    `,
  parameters: createAssignmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateAssignmentGroupData, "url"> ) => {
    try {
      const { data } = await createAssignmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    