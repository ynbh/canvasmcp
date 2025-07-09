
import { tool } from "ai";
import { getUserInACourseLevelAssignmentDataDataSchema } from "./aitm.schema.ts";
import { getUserInACourseLevelAssignmentData, GetUserInACourseLevelAssignmentDataData } from "..";

export default tool({
  description: `
  Get user-in-a-course-level assignment data
Returns a list of assignments for the course sorted by
due date. For
each assignment returns basic assignment information, the grade breakdown
(including
the student's actual grade), and the basic submission
information for the student's submission if it
exists.
    `,
  parameters: getUserInACourseLevelAssignmentDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetUserInACourseLevelAssignmentDataData, "url"> ) => {
    try {
      const { data } = await getUserInACourseLevelAssignmentData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    