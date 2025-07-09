
import { tool } from "ai";
import { listAssignmentSubmissionsCoursesDataSchema } from "./aitm.schema.ts";
import { listAssignmentSubmissionsCourses, ListAssignmentSubmissionsCoursesData } from "..";

export default tool({
  description: `
  List assignment submissions
A paginated list of all existing submissions for an assignment.
    `,
  parameters: listAssignmentSubmissionsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAssignmentSubmissionsCoursesData, "url"> ) => {
    try {
      const { data } = await listAssignmentSubmissionsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    