
import { tool } from "ai";
import { bulkSelectProvisionalGradesDataSchema } from "./aitm.schema.ts";
import { bulkSelectProvisionalGrades, BulkSelectProvisionalGradesData } from "..";

export default tool({
  description: `
  Bulk select provisional grades
Choose which provisional grades will be received by associated
students for an assignment.
The caller must be the final grader for the assignment or an admin with
:select_final_grade rights.
    `,
  parameters: bulkSelectProvisionalGradesDataSchema.omit({ url: true }),
  execute: async (args : Omit<BulkSelectProvisionalGradesData, "url"> ) => {
    try {
      const { data } = await bulkSelectProvisionalGrades(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    