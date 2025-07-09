
import { tool } from "ai";
import { listFilesCoursesDataSchema } from "./aitm.schema.ts";
import { listFilesCourses, ListFilesCoursesData } from "..";

export default tool({
  description: `
  List files
Returns the paginated list of files for the folder or course.
    `,
  parameters: listFilesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFilesCoursesData, "url"> ) => {
    try {
      const { data } = await listFilesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    