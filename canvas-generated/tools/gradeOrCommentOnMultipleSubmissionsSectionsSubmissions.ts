
import { tool } from "ai";
import { gradeOrCommentOnMultipleSubmissionsSectionsSubmissionsDataSchema } from "./aitm.schema.ts";
import { gradeOrCommentOnMultipleSubmissionsSectionsSubmissions, GradeOrCommentOnMultipleSubmissionsSectionsSubmissionsData } from "..";

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
  parameters: gradeOrCommentOnMultipleSubmissionsSectionsSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GradeOrCommentOnMultipleSubmissionsSectionsSubmissionsData, "url"> ) => {
    try {
      const { data } = await gradeOrCommentOnMultipleSubmissionsSectionsSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    