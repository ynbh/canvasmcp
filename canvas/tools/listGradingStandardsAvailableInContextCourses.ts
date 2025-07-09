
import { tool } from "ai";
import { listGradingStandardsAvailableInContextCoursesDataSchema } from "./aitm.schema.ts";
import { listGradingStandardsAvailableInContextCourses, ListGradingStandardsAvailableInContextCoursesData } from "..";

export default tool({
  description: `
  List the grading standards available in a context.
Returns the paginated list of grading standards
for the given context that are visible to the user.
    `,
  parameters: listGradingStandardsAvailableInContextCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGradingStandardsAvailableInContextCoursesData, "url"> ) => {
    try {
      const { data } = await listGradingStandardsAvailableInContextCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    