
import { tool } from "ai";
import { updateUserSettingsDataSchema } from "./aitm.schema.ts";
import { updateUserSettings, UpdateUserSettingsData } from "..";

export default tool({
  description: `
  Update user settings.
Update an existing user's settings.
    `,
  parameters: updateUserSettingsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateUserSettingsData, "url"> ) => {
    try {
      const { data } = await updateUserSettings(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    