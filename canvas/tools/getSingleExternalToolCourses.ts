
import { tool } from "ai";
import { getSingleExternalToolCoursesDataSchema } from "./aitm.schema.ts";
import { getSingleExternalToolCourses, GetSingleExternalToolCoursesData } from "..";

export default tool({
  description: `
  Get a single external tool
Returns the specified external tool.
    `,
  parameters: getSingleExternalToolCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleExternalToolCoursesData, "url"> ) => {
    try {
      const { data } = await getSingleExternalToolCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    