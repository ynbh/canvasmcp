
import { tool } from "ai";
import { getCourseLevelStudentSummaryDataDataSchema } from "./aitm.schema.ts";
import { getCourseLevelStudentSummaryData, GetCourseLevelStudentSummaryDataData } from "..";

export default tool({
  description: `
  Get course-level student summary data
Returns a summary of per-user access information for all
students in
a course. This includes total page views, total participations, and a
breakdown of
on-time/late status for all homework submissions in the course.

Each student's summary also
includes the maximum number of page views and
participations by any student in the course, which may
be useful for some
visualizations (since determining maximums client side can be tricky
with
pagination).
    `,
  parameters: getCourseLevelStudentSummaryDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCourseLevelStudentSummaryDataData, "url"> ) => {
    try {
      const { data } = await getCourseLevelStudentSummaryData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    