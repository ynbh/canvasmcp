
import { tool } from "ai";
import { listAssignmentsDataSchema } from "./aitm.schema.ts";
import { listAssignments, ListAssignmentsData } from "..";

export default tool({
  description: `
  List assignments
Returns the paginated list of assignments for the current context.
    `,
  parameters: listAssignmentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAssignmentsData, "url"> ) => {
    try {
      const { data } = await listAssignments(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    