
import { tool } from "ai";
import { listRubricsCoursesDataSchema } from "./aitm.schema.ts";
import { listRubricsCourses, ListRubricsCoursesData } from "..";

export default tool({
  description: `
  List rubrics
Returns the paginated list of active rubrics for the current context.
    `,
  parameters: listRubricsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListRubricsCoursesData, "url"> ) => {
    try {
      const { data } = await listRubricsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    