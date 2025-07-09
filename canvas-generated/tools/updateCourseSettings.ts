
import { tool } from "ai";
import { updateCourseSettingsDataSchema } from "./aitm.schema.ts";
import { updateCourseSettings, UpdateCourseSettingsData } from "..";

export default tool({
  description: `
  Update course settings
Can update the following course settings:
    `,
  parameters: updateCourseSettingsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCourseSettingsData, "url"> ) => {
    try {
      const { data } = await updateCourseSettings(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    