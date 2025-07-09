
import { tool } from "ai";
import { listPreferencesCommunicationChannelIdDataSchema } from "./aitm.schema.ts";
import { listPreferencesCommunicationChannelId, ListPreferencesCommunicationChannelIdData } from "..";

export default tool({
  description: `
  List preferences
Fetch all preferences for the given communication channel
    `,
  parameters: listPreferencesCommunicationChannelIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPreferencesCommunicationChannelIdData, "url"> ) => {
    try {
      const { data } = await listPreferencesCommunicationChannelId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    