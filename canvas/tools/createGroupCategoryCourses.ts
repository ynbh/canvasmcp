
import { tool } from "ai";
import { createGroupCategoryCoursesDataSchema } from "./aitm.schema.ts";
import { createGroupCategoryCourses, CreateGroupCategoryCoursesData } from "..";

export default tool({
  description: `
  Create a Group Category
Create a new group category
    `,
  parameters: createGroupCategoryCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateGroupCategoryCoursesData, "url"> ) => {
    try {
      const { data } = await createGroupCategoryCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    