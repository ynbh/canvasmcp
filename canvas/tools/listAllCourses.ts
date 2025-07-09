
import { tool } from "ai";
import { listAllCoursesDataSchema } from "./aitm.schema.ts";
import { listAllCourses, ListAllCoursesData } from "..";

export default tool({
  description: `
  List all courses
A paginated list of all courses visible in the public index
    `,
  parameters: listAllCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAllCoursesData, "url"> ) => {
    try {
      const { data } = await listAllCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    