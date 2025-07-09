
import { tool } from "ai";
import { createPageCoursesDataSchema } from "./aitm.schema.ts";
import { createPageCourses, CreatePageCoursesData } from "..";

export default tool({
  description: `
  Create page
Create a new wiki page
    `,
  parameters: createPageCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreatePageCoursesData, "url"> ) => {
    try {
      const { data } = await createPageCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    