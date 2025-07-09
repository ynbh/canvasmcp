
import { tool } from "ai";
import { gradeOrCommentOnMultipleSubmissionsCoursesSubmissionsDataSchema } from "./aitm.schema.ts";
import { gradeOrCommentOnMultipleSubmissionsCoursesSubmissions, GradeOrCommentOnMultipleSubmissionsCoursesSubmissionsData } from "..";

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
  parameters: gradeOrCommentOnMultipleSubmissionsCoursesSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GradeOrCommentOnMultipleSubmissionsCoursesSubmissionsData, "url"> ) => {
    try {
      const { data } = await gradeOrCommentOnMultipleSubmissionsCoursesSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    