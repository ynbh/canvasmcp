
import { tool } from "ai";
import { revertToRevisionCoursesDataSchema } from "./aitm.schema.ts";
import { revertToRevisionCourses, RevertToRevisionCoursesData } from "..";

export default tool({
  description: `
  Revert to revision
Revert a page to a prior revision.
    `,
  parameters: revertToRevisionCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<RevertToRevisionCoursesData, "url"> ) => {
    try {
      const { data } = await revertToRevisionCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    