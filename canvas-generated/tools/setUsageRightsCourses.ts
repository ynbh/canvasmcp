
import { tool } from "ai";
import { setUsageRightsCoursesDataSchema } from "./aitm.schema.ts";
import { setUsageRightsCourses, SetUsageRightsCoursesData } from "..";

export default tool({
  description: `
  Set usage rights
Sets copyright and license information for one or more files
    `,
  parameters: setUsageRightsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetUsageRightsCoursesData, "url"> ) => {
    try {
      const { data } = await setUsageRightsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    