
import { tool } from "ai";
import { daysInGradebookHistoryForThisCourseDataSchema } from "./aitm.schema.ts";
import { daysInGradebookHistoryForThisCourse, DaysInGradebookHistoryForThisCourseData } from "..";

export default tool({
  description: `
  Days in gradebook history for this course
Returns a map of dates to grader/assignment groups
    `,
  parameters: daysInGradebookHistoryForThisCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<DaysInGradebookHistoryForThisCourseData, "url"> ) => {
    try {
      const { data } = await daysInGradebookHistoryForThisCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    