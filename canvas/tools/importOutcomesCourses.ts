
import { tool } from "ai";
import { importOutcomesCoursesDataSchema } from "./aitm.schema.ts";
import { importOutcomesCourses, ImportOutcomesCoursesData } from "..";

export default tool({
  description: `
  Import Outcomes
Import outcomes into Canvas.

For more information on the format that's expected
here, please see the
"Outcomes CSV" section in the API docs.
    `,
  parameters: importOutcomesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ImportOutcomesCoursesData, "url"> ) => {
    try {
      const { data } = await importOutcomesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    