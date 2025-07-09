
import { tool } from "ai";
import { listAssignmentSubmissionsSectionsDataSchema } from "./aitm.schema.ts";
import { listAssignmentSubmissionsSections, ListAssignmentSubmissionsSectionsData } from "..";

export default tool({
  description: `
  List assignment submissions
A paginated list of all existing submissions for an assignment.
    `,
  parameters: listAssignmentSubmissionsSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAssignmentSubmissionsSectionsData, "url"> ) => {
    try {
      const { data } = await listAssignmentSubmissionsSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    