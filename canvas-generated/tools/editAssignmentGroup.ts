
import { tool } from "ai";
import { editAssignmentGroupDataSchema } from "./aitm.schema.ts";
import { editAssignmentGroup, EditAssignmentGroupData } from "..";

export default tool({
  description: `
  Edit an Assignment Group
Modify an existing Assignment Group.
Accepts the same parameters as
Assignment Group creation
    `,
  parameters: editAssignmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditAssignmentGroupData, "url"> ) => {
    try {
      const { data } = await editAssignmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    