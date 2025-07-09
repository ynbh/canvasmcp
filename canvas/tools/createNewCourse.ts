
import { tool } from "ai";
import { createNewCourseDataSchema } from "./aitm.schema.ts";
import { createNewCourse, CreateNewCourseData } from "..";

export default tool({
  description: `
  Create a new course
Create a new course
    `,
  parameters: createNewCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateNewCourseData, "url"> ) => {
    try {
      const { data } = await createNewCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    