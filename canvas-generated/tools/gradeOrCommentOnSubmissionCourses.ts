
import { tool } from "ai";
import { gradeOrCommentOnSubmissionCoursesDataSchema } from "./aitm.schema.ts";
import { gradeOrCommentOnSubmissionCourses, GradeOrCommentOnSubmissionCoursesData } from "..";

export default tool({
  description: `
  Grade or comment on a submission
Comment on and/or update the grading for a student's assignment
submission. If any submission or rubric_assessment arguments are provided, the user must have
permission to manage grades in the appropriate context (course or section).
    `,
  parameters: gradeOrCommentOnSubmissionCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GradeOrCommentOnSubmissionCoursesData, "url"> ) => {
    try {
      const { data } = await gradeOrCommentOnSubmissionCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    