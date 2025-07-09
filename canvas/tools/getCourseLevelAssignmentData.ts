
import { tool } from "ai";
import { getCourseLevelAssignmentDataDataSchema } from "./aitm.schema.ts";
import { getCourseLevelAssignmentData, GetCourseLevelAssignmentDataData } from "..";

export default tool({
  description: `
  Get course-level assignment data
Returns a list of assignments for the course sorted by due date.
For
each assignment returns basic assignment information, the grade breakdown,
and a breakdown of
on-time/late status of homework submissions.
    `,
  parameters: getCourseLevelAssignmentDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCourseLevelAssignmentDataData, "url"> ) => {
    try {
      const { data } = await getCourseLevelAssignmentData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    