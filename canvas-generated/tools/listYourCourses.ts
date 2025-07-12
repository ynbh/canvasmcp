
import { tool } from "ai";
import { listYourCoursesDataSchema } from "./aitm.schema.ts";
import { listYourCourses, ListYourCoursesData } from "..";

export default tool({
  description: `
  List your courses
Returns the paginated list of active courses for the current user. Includes other information like courseID. 
    `,
  parameters: listYourCoursesDataSchema.omit({ url: true }),
  execute: async (args: Omit<ListYourCoursesData, "url">) => {
    try {
      const { data } = await listYourCourses(args);

      // const today = new Date();
      // const iso = today.toISOString();

      // const currentSem = data?.filter(course => {
      //   const t  = course?.term; 

      //   return (!t.start_at || iso >= t.start_at) &&
      //      (!t.end_at   || iso <  t.end_at);
      // })

      const filtered = data?.map(course => ({
        id: course?.id != null ? course.id.toString() : "", 
        name: course.name,
      }));

      return filtered;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
