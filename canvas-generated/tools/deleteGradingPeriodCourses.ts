
import { tool } from "ai";
import { deleteGradingPeriodCoursesDataSchema } from "./aitm.schema.ts";
import { deleteGradingPeriodCourses, DeleteGradingPeriodCoursesData } from "..";

export default tool({
  description: `
  Delete a grading period
<b>204 No Content</b> response code is returned if the deletion
was
successful.
    `,
  parameters: deleteGradingPeriodCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteGradingPeriodCoursesData, "url"> ) => {
    try {
      const { data } = await deleteGradingPeriodCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    