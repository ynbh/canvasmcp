
import { tool } from "ai";
import { selectProvisionalGradeDataSchema } from "./aitm.schema.ts";
import { selectProvisionalGrade, SelectProvisionalGradeData } from "..";

export default tool({
  description: `
  Select provisional grade
Choose which provisional grade the student should receive for a
submission.
The caller must be the final grader for the assignment or an admin with
:select_final_grade rights.
    `,
  parameters: selectProvisionalGradeDataSchema.omit({ url: true }),
  execute: async (args : Omit<SelectProvisionalGradeData, "url"> ) => {
    try {
      const { data } = await selectProvisionalGrade(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    