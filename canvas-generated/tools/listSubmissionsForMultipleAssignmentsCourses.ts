
import { tool } from "ai";
import { listSubmissionsForMultipleAssignmentsCoursesDataSchema } from "./aitm.schema.ts";
import { listSubmissionsForMultipleAssignmentsCourses, ListSubmissionsForMultipleAssignmentsCoursesData } from "..";

export default tool({
  description: `
  List submissions for multiple assignments
A paginated list of all existing submissions for a given
set of students and assignments.
    `,
  parameters: listSubmissionsForMultipleAssignmentsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListSubmissionsForMultipleAssignmentsCoursesData, "url"> ) => {
    try {
      const { data } = await listSubmissionsForMultipleAssignmentsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    