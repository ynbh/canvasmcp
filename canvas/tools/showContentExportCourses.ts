
import { tool } from "ai";
import { showContentExportCoursesDataSchema } from "./aitm.schema.ts";
import { showContentExportCourses, ShowContentExportCoursesData } from "..";

export default tool({
  description: `
  Show content export
Get information about a single content export.
    `,
  parameters: showContentExportCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowContentExportCoursesData, "url"> ) => {
    try {
      const { data } = await showContentExportCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    