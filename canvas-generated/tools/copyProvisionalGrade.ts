
import { tool } from "ai";
import { copyProvisionalGradeDataSchema } from "./aitm.schema.ts";
import { copyProvisionalGrade, CopyProvisionalGradeData } from "..";

export default tool({
  description: `
  Copy provisional grade
Given a provisional grade, copy the grade (and associated submission comments
and rubric assessments)
to a "final" mark which can be edited or commented upon by a moderator prior
to publication of grades.

Notes:
* The student must be in the moderation set for the assignment.
*
The newly created grade will be selected.
* The caller must have "Moderate Grades" rights in the
course.
    `,
  parameters: copyProvisionalGradeDataSchema.omit({ url: true }),
  execute: async (args : Omit<CopyProvisionalGradeData, "url"> ) => {
    try {
      const { data } = await copyProvisionalGrade(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    