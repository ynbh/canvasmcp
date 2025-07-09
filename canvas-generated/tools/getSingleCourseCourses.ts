
import { tool } from "ai";
import { getSingleCourseCoursesDataSchema } from "./aitm.schema.ts";
import { getSingleCourseCourses, GetSingleCourseCoursesData } from "..";

export default tool({
  description: `
  Get a single course
Return information on a single course.

Accepts the same include[] parameters as
the list action plus:
    `,
  parameters: getSingleCourseCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleCourseCoursesData, "url"> ) => {
    try {
      const { data } = await getSingleCourseCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    