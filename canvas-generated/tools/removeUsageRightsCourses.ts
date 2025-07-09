
import { tool } from "ai";
import { removeUsageRightsCoursesDataSchema } from "./aitm.schema.ts";
import { removeUsageRightsCourses, RemoveUsageRightsCoursesData } from "..";

export default tool({
  description: `
  Remove usage rights
Removes copyright and license information associated with one or more files
    `,
  parameters: removeUsageRightsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveUsageRightsCoursesData, "url"> ) => {
    try {
      const { data } = await removeUsageRightsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    