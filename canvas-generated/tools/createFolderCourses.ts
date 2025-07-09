
import { tool } from "ai";
import { createFolderCoursesDataSchema } from "./aitm.schema.ts";
import { createFolderCourses, CreateFolderCoursesData } from "..";

export default tool({
  description: `
  Create folder
Creates a folder in the specified context
    `,
  parameters: createFolderCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateFolderCoursesData, "url"> ) => {
    try {
      const { data } = await createFolderCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    