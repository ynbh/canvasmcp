
import { tool } from "ai";
import { detailsForGivenDateInGradebookHistoryForThisCourseDataSchema } from "./aitm.schema.ts";
import { detailsForGivenDateInGradebookHistoryForThisCourse, DetailsForGivenDateInGradebookHistoryForThisCourseData } from "..";

export default tool({
  description: `
  Details for a given date in gradebook history for this course
Returns the graders who worked on this
day, along with the assignments they worked on.
More details can be obtained by selecting a grader
and assignment and calling the
'submissions' api endpoint for a given date.
    `,
  parameters: detailsForGivenDateInGradebookHistoryForThisCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<DetailsForGivenDateInGradebookHistoryForThisCourseData, "url"> ) => {
    try {
      const { data } = await detailsForGivenDateInGradebookHistoryForThisCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    