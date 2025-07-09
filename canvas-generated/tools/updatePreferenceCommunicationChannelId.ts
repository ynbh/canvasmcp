
import { tool } from "ai";
import { updatePreferenceCommunicationChannelIdDataSchema } from "./aitm.schema.ts";
import { updatePreferenceCommunicationChannelId, UpdatePreferenceCommunicationChannelIdData } from "..";

export default tool({
  description: `
  Update a preference
Change the preference for a single notification for a single communication
channel
    `,
  parameters: updatePreferenceCommunicationChannelIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdatePreferenceCommunicationChannelIdData, "url"> ) => {
    try {
      const { data } = await updatePreferenceCommunicationChannelId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    