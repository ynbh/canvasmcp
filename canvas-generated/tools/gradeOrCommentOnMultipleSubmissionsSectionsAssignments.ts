
import { tool } from "ai";
import { gradeOrCommentOnMultipleSubmissionsSectionsAssignmentsDataSchema } from "./aitm.schema.ts";
import { gradeOrCommentOnMultipleSubmissionsSectionsAssignments, GradeOrCommentOnMultipleSubmissionsSectionsAssignmentsData } from "..";

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
  parameters: gradeOrCommentOnMultipleSubmissionsSectionsAssignmentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GradeOrCommentOnMultipleSubmissionsSectionsAssignmentsData, "url"> ) => {
    try {
      const { data } = await gradeOrCommentOnMultipleSubmissionsSectionsAssignments(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    