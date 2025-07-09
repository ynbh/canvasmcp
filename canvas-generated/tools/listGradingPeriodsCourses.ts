
import { tool } from "ai";
import { listGradingPeriodsCoursesDataSchema } from "./aitm.schema.ts";
import { listGradingPeriodsCourses, ListGradingPeriodsCoursesData } from "..";

export default tool({
  description: `
  List grading periods
Returns the paginated list of grading periods for the current course.
    `,
  parameters: listGradingPeriodsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGradingPeriodsCoursesData, "url"> ) => {
    try {
      const { data } = await listGradingPeriodsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    