
import { tool } from "ai";
import { enrollUserCoursesDataSchema } from "./aitm.schema.ts";
import { enrollUserCourses, EnrollUserCoursesData } from "..";

export default tool({
  description: `
  Enroll a user
Create a new user enrollment for a course or section.
    `,
  parameters: enrollUserCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<EnrollUserCoursesData, "url"> ) => {
    try {
      const { data } = await enrollUserCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    