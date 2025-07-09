
import { tool } from "ai";
import { listEnabledFeaturesCoursesDataSchema } from "./aitm.schema.ts";
import { listEnabledFeaturesCourses, ListEnabledFeaturesCoursesData } from "..";

export default tool({
  description: `
  List enabled features
A paginated list of all features that are enabled on a given Account, Course,
or User.
Only the feature names are returned.
    `,
  parameters: listEnabledFeaturesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEnabledFeaturesCoursesData, "url"> ) => {
    try {
      const { data } = await listEnabledFeaturesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    