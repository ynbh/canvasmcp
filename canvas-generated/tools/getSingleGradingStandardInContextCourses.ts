
import { tool } from "ai";
import { getSingleGradingStandardInContextCoursesDataSchema } from "./aitm.schema.ts";
import { getSingleGradingStandardInContextCourses, GetSingleGradingStandardInContextCoursesData } from "..";

export default tool({
  description: `
  Get a single grading standard in a context.
Returns a grading standard for the given context that is
visible to the user.
    `,
  parameters: getSingleGradingStandardInContextCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleGradingStandardInContextCoursesData, "url"> ) => {
    try {
      const { data } = await getSingleGradingStandardInContextCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    