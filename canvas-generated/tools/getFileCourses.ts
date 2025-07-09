
import { tool } from "ai";
import { getFileCoursesDataSchema } from "./aitm.schema.ts";
import { getFileCourses, GetFileCoursesData } from "..";

export default tool({
  description: `
  Get file
Returns the standard attachment json object
    `,
  parameters: getFileCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFileCoursesData, "url"> ) => {
    try {
      const { data } = await getFileCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    