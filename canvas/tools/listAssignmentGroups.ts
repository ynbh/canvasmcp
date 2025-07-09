
import { tool } from "ai";
import { listAssignmentGroupsDataSchema } from "./aitm.schema.ts";
import { listAssignmentGroups, ListAssignmentGroupsData } from "..";

export default tool({
  description: `
  List assignment groups
Returns the paginated list of assignment groups for the current context.
The
returned groups are sorted by their position field.
    `,
  parameters: listAssignmentGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAssignmentGroupsData, "url"> ) => {
    try {
      const { data } = await listAssignmentGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    