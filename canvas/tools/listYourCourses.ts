
import { tool } from "ai";
import { listYourCoursesDataSchema } from "./aitm.schema.ts";
import { listYourCourses, ListYourCoursesData } from "..";

export default tool({
  description: `
  List your courses
Returns the paginated list of active courses for the current user. Includes other information like courseID. 
    `,
  parameters: listYourCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListYourCoursesData, "url"> ) => {
    try {
      const { data } = await listYourCourses(args);
      const filtered = data?.map((course) => ({ id: course.id?.toString(), name: course.name }))
      console.log("gathered courses", filtered);
      return filtered;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    