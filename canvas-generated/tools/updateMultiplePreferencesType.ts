
import { tool } from "ai";
import { updateMultiplePreferencesTypeDataSchema } from "./aitm.schema.ts";
import { updateMultiplePreferencesType, UpdateMultiplePreferencesTypeData } from "..";

export default tool({
  description: `
  Update multiple preferences
Change the preferences for multiple notifications for a single
communication channel at once
    `,
  parameters: updateMultiplePreferencesTypeDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMultiplePreferencesTypeData, "url"> ) => {
    try {
      const { data } = await updateMultiplePreferencesType(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    