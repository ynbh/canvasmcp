
import { tool } from "ai";
import { listSubmissionsForMultipleAssignmentsSectionsDataSchema } from "./aitm.schema.ts";
import { listSubmissionsForMultipleAssignmentsSections, ListSubmissionsForMultipleAssignmentsSectionsData } from "..";

export default tool({
  description: `
  List submissions for multiple assignments
A paginated list of all existing submissions for a given
set of students and assignments.
    `,
  parameters: listSubmissionsForMultipleAssignmentsSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListSubmissionsForMultipleAssignmentsSectionsData, "url"> ) => {
    try {
      const { data } = await listSubmissionsForMultipleAssignmentsSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    