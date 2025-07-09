
import { tool } from "ai";
import { listAssignmentOverridesDataSchema } from "./aitm.schema.ts";
import { listAssignmentOverrides, ListAssignmentOverridesData } from "..";

export default tool({
  description: `
  List assignment overrides
Returns the paginated list of overrides for this assignment that
target
sections/groups/students visible to the current user.
    `,
  parameters: listAssignmentOverridesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAssignmentOverridesData, "url"> ) => {
    try {
      const { data } = await listAssignmentOverrides(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    