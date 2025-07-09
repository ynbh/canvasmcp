
import { tool } from "ai";
import { showProvisionalGradeStatusForStudentDataSchema } from "./aitm.schema.ts";
import { showProvisionalGradeStatusForStudent, ShowProvisionalGradeStatusForStudentData } from "..";

export default tool({
  description: `
  Show provisional grade status for a student
Tell whether the student's submission needs one or more
provisional grades.
    `,
  parameters: showProvisionalGradeStatusForStudentDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowProvisionalGradeStatusForStudentData, "url"> ) => {
    try {
      const { data } = await showProvisionalGradeStatusForStudent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    