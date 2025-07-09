
import { tool } from "ai";
import { updateCreateFrontPageCoursesDataSchema } from "./aitm.schema.ts";
import { updateCreateFrontPageCourses, UpdateCreateFrontPageCoursesData } from "..";

export default tool({
  description: `
  Update/create front page
Update the title or contents of the front page
    `,
  parameters: updateCreateFrontPageCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCreateFrontPageCoursesData, "url"> ) => {
    try {
      const { data } = await updateCreateFrontPageCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    