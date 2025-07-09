
import { tool } from "ai";
import { listPreferencesTypeDataSchema } from "./aitm.schema.ts";
import { listPreferencesType, ListPreferencesTypeData } from "..";

export default tool({
  description: `
  List preferences
Fetch all preferences for the given communication channel
    `,
  parameters: listPreferencesTypeDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPreferencesTypeData, "url"> ) => {
    try {
      const { data } = await listPreferencesType(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    