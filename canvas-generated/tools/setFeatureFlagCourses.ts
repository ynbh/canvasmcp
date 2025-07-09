
import { tool } from "ai";
import { setFeatureFlagCoursesDataSchema } from "./aitm.schema.ts";
import { setFeatureFlagCourses, SetFeatureFlagCoursesData } from "..";

export default tool({
  description: `
  Set feature flag
Set a feature flag for a given Account, Course, or User. This call will fail if a
parent account sets
a feature flag for the same feature in any state other than "allowed".
    `,
  parameters: setFeatureFlagCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetFeatureFlagCoursesData, "url"> ) => {
    try {
      const { data } = await setFeatureFlagCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    