
import { tool } from "ai";
import { resetCourseDataSchema } from "./aitm.schema.ts";
import { resetCourse, ResetCourseData } from "..";

export default tool({
  description: `
  Reset a course
Deletes the current course, and creates a new equivalent course with
no content, but
all sections and users moved over.
    `,
  parameters: resetCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<ResetCourseData, "url"> ) => {
    try {
      const { data } = await resetCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    