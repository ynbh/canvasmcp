
import { tool } from "ai";
import { listAssignmentsDataSchema } from "./aitm.schema.ts";
import { listAssignments, ListAssignmentsData } from "..";

export default tool({
  description: `
List Assignment IDs
Returns the paginated list of assignment IDs for the current context.
    `,
  parameters: listAssignmentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAssignmentsData, "url"> ) => {
    try {
      const { data } = await listAssignments(args);
      // extract only the IDs and name for each assignment 
      const filtered = data?.map(assignment => ({
        id: assignment?.id != null ? assignment.id : "", 
        name: assignment.name 
      }))
      return filtered;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    