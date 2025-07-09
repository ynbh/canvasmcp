
import { tool } from "ai";
import { showProvisionalGradeStatusForStudentAnonymousDataSchema } from "./aitm.schema.ts";
import { showProvisionalGradeStatusForStudentAnonymous, ShowProvisionalGradeStatusForStudentAnonymousData } from "..";

export default tool({
  description: `
  Show provisional grade status for a student
Determine whether or not the student's submission needs
one or more provisional grades.
    `,
  parameters: showProvisionalGradeStatusForStudentAnonymousDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowProvisionalGradeStatusForStudentAnonymousData, "url"> ) => {
    try {
      const { data } = await showProvisionalGradeStatusForStudentAnonymous(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    