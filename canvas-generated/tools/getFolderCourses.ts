
import { tool } from "ai";
import { getFolderCoursesDataSchema } from "./aitm.schema.ts";
import { getFolderCourses, GetFolderCoursesData } from "..";

export default tool({
  description: `
  Get folder
Returns the details for a folder

You can get the root folder from a context by using
'root' as the :id.
For example, you could get the root folder for a course like:
    `,
  parameters: getFolderCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFolderCoursesData, "url"> ) => {
    try {
      const { data } = await getFolderCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    