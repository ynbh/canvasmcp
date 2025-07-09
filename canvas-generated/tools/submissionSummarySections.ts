
import { tool } from "ai";
import { submissionSummarySectionsDataSchema } from "./aitm.schema.ts";
import { submissionSummarySections, SubmissionSummarySectionsData } from "..";

export default tool({
  description: `
  Submission Summary
Returns the number of submissions for the given assignment based on gradeable
students
that fall into three categories: graded, ungraded, not submitted.
    `,
  parameters: submissionSummarySectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<SubmissionSummarySectionsData, "url"> ) => {
    try {
      const { data } = await submissionSummarySections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    