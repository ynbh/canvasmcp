
import { tool } from "ai";
import { courseActivityStreamSummaryDataSchema } from "./aitm.schema.ts";
import { courseActivityStreamSummary, CourseActivityStreamSummaryData } from "..";

export default tool({
  description: `
  Course activity stream summary
Returns a summary of the current user's course-specific activity
stream.

For full documentation, see the API documentation for the user activity
stream summary, in
the user api.
    `,
  parameters: courseActivityStreamSummaryDataSchema.omit({ url: true }),
  execute: async (args : Omit<CourseActivityStreamSummaryData, "url"> ) => {
    try {
      const { data } = await courseActivityStreamSummary(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    