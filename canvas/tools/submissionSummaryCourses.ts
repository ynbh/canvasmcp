
import { tool } from "ai";
import { submissionSummaryCoursesDataSchema } from "./aitm.schema.ts";
import { submissionSummaryCourses, SubmissionSummaryCoursesData } from "..";

export default tool({
  description: `
  Submission Summary
Returns the number of submissions for the given assignment based on gradeable
students
that fall into three categories: graded, ungraded, not submitted.
    `,
  parameters: submissionSummaryCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<SubmissionSummaryCoursesData, "url"> ) => {
    try {
      const { data } = await submissionSummaryCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    