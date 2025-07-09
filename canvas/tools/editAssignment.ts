
import { tool } from "ai";
import { editAssignmentDataSchema } from "./aitm.schema.ts";
import { editAssignment, EditAssignmentData } from "..";

export default tool({
  description: `
  Edit an assignment
Modify an existing assignment.

If the assignment [assignment_overrides] key is
absent, any existing
overrides are kept as is. If the assignment [assignment_overrides] key
is
present, existing overrides are updated or deleted (and new ones created,
as necessary) to match
the provided list.
    `,
  parameters: editAssignmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditAssignmentData, "url"> ) => {
    try {
      const { data } = await editAssignment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    