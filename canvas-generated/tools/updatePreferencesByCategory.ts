
import { tool } from "ai";
import { updatePreferencesByCategoryDataSchema } from "./aitm.schema.ts";
import { updatePreferencesByCategory, UpdatePreferencesByCategoryData } from "..";

export default tool({
  description: `
  Update preferences by category
Change the preferences for multiple notifications based on the
category for a single communication channel
    `,
  parameters: updatePreferencesByCategoryDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdatePreferencesByCategoryData, "url"> ) => {
    try {
      const { data } = await updatePreferencesByCategory(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    