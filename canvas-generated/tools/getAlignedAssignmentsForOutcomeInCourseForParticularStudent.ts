
import { tool } from "ai";
import { getAlignedAssignmentsForOutcomeInCourseForParticularStudentDataSchema } from "./aitm.schema.ts";
import { getAlignedAssignmentsForOutcomeInCourseForParticularStudent, GetAlignedAssignmentsForOutcomeInCourseForParticularStudentData } from "..";

export default tool({
  description: `
  Get aligned assignments for an outcome in a course for a particular student
    `,
  parameters: getAlignedAssignmentsForOutcomeInCourseForParticularStudentDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAlignedAssignmentsForOutcomeInCourseForParticularStudentData, "url"> ) => {
    try {
      const { data } = await getAlignedAssignmentsForOutcomeInCourseForParticularStudent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    