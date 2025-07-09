
import { tool } from "ai";
import { listFeaturesCoursesDataSchema } from "./aitm.schema.ts";
import { listFeaturesCourses, ListFeaturesCoursesData } from "..";

export default tool({
  description: `
  List features
A paginated list of all features that apply to a given Account, Course, or User.
    `,
  parameters: listFeaturesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFeaturesCoursesData, "url"> ) => {
    try {
      const { data } = await listFeaturesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    