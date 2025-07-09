
import { tool } from "ai";
import { updateMultiplePreferencesCommunicationChannelIdDataSchema } from "./aitm.schema.ts";
import { updateMultiplePreferencesCommunicationChannelId, UpdateMultiplePreferencesCommunicationChannelIdData } from "..";

export default tool({
  description: `
  Update multiple preferences
Change the preferences for multiple notifications for a single
communication channel at once
    `,
  parameters: updateMultiplePreferencesCommunicationChannelIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMultiplePreferencesCommunicationChannelIdData, "url"> ) => {
    try {
      const { data } = await updateMultiplePreferencesCommunicationChannelId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    