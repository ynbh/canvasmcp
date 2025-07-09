
import { tool } from "ai";
import { deletePageCoursesDataSchema } from "./aitm.schema.ts";
import { deletePageCourses, DeletePageCoursesData } from "..";

export default tool({
  description: `
  Delete page
Delete a wiki page
    `,
  parameters: deletePageCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePageCoursesData, "url"> ) => {
    try {
      const { data } = await deletePageCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    