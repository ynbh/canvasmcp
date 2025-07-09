
import { tool } from "ai";
import { updateTabForCourseDataSchema } from "./aitm.schema.ts";
import { updateTabForCourse, UpdateTabForCourseData } from "..";

export default tool({
  description: `
  Update a tab for a course
Home and Settings tabs are not manageable, and can't be hidden or
moved

Returns a tab object
    `,
  parameters: updateTabForCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateTabForCourseData, "url"> ) => {
    try {
      const { data } = await updateTabForCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    