
import { tool } from "ai";
import { gradeOrCommentOnSubmissionSectionsDataSchema } from "./aitm.schema.ts";
import { gradeOrCommentOnSubmissionSections, GradeOrCommentOnSubmissionSectionsData } from "..";

export default tool({
  description: `
  Grade or comment on a submission
Comment on and/or update the grading for a student's assignment
submission.
If any submission or rubric_assessment arguments are provided, the user
must have
permission to manage grades in the appropriate context (course or
section).
    `,
  parameters: gradeOrCommentOnSubmissionSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GradeOrCommentOnSubmissionSectionsData, "url"> ) => {
    try {
      const { data } = await gradeOrCommentOnSubmissionSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    