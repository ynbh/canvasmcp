
import { tool } from "ai";
import { showFrontPageCoursesDataSchema } from "./aitm.schema.ts";
import { showFrontPageCourses, ShowFrontPageCoursesData } from "..";

export default tool({
  description: `
  Show front page
Retrieve the content of the front page
    `,
  parameters: showFrontPageCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowFrontPageCoursesData, "url"> ) => {
    try {
      const { data } = await showFrontPageCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    