
import { tool } from "ai";
import { listGroupCategoriesForContextCoursesDataSchema } from "./aitm.schema.ts";
import { listGroupCategoriesForContextCourses, ListGroupCategoriesForContextCoursesData } from "..";

export default tool({
  description: `
  List group categories for a context
Returns a paginated list of group categories in a context
    `,
  parameters: listGroupCategoriesForContextCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGroupCategoriesForContextCoursesData, "url"> ) => {
    try {
      const { data } = await listGroupCategoriesForContextCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    