
import { tool } from "ai";
import { updateCreatePageCoursesDataSchema } from "./aitm.schema.ts";
import { updateCreatePageCourses, UpdateCreatePageCoursesData } from "..";

export default tool({
  description: `
  Update/create page
Update the title or contents of a wiki page
    `,
  parameters: updateCreatePageCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCreatePageCoursesData, "url"> ) => {
    try {
      const { data } = await updateCreatePageCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    