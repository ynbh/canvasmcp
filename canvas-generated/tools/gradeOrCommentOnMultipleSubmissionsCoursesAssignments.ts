
import { tool } from "ai";
import { gradeOrCommentOnMultipleSubmissionsCoursesAssignmentsDataSchema } from "./aitm.schema.ts";
import { gradeOrCommentOnMultipleSubmissionsCoursesAssignments, GradeOrCommentOnMultipleSubmissionsCoursesAssignmentsData } from "..";

export default tool({
  description: `
  Grade or comment on multiple submissions
Update the grading and comments on multiple student's
assignment
submissions in an asynchronous job.

The user must have permission to manage grades in
the appropriate context
(course or section).
    `,
  parameters: gradeOrCommentOnMultipleSubmissionsCoursesAssignmentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GradeOrCommentOnMultipleSubmissionsCoursesAssignmentsData, "url"> ) => {
    try {
      const { data } = await gradeOrCommentOnMultipleSubmissionsCoursesAssignments(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    