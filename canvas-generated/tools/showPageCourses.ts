
import { tool } from "ai";
import { showPageCoursesDataSchema } from "./aitm.schema.ts";
import { showPageCourses, ShowPageCoursesData } from "..";

export default tool({
  description: `
  Show page
Retrieve the content of a wiki page
    `,
  parameters: showPageCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowPageCoursesData, "url"> ) => {
    try {
      const { data } = await showPageCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    