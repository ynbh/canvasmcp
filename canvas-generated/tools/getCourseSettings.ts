
import { tool } from "ai";
import { getCourseSettingsDataSchema } from "./aitm.schema.ts";
import { getCourseSettings, GetCourseSettingsData } from "..";

export default tool({
  description: `
  Get course settings
Returns some of a course's settings.
    `,
  parameters: getCourseSettingsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCourseSettingsData, "url"> ) => {
    try {
      const { data } = await getCourseSettings(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    