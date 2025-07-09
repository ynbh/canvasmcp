
import { tool } from "ai";
import { getPreferenceCommunicationChannelIdDataSchema } from "./aitm.schema.ts";
import { getPreferenceCommunicationChannelId, GetPreferenceCommunicationChannelIdData } from "..";

export default tool({
  description: `
  Get a preference
Fetch the preference for the given notification for the given communicaiton channel
    `,
  parameters: getPreferenceCommunicationChannelIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetPreferenceCommunicationChannelIdData, "url"> ) => {
    try {
      const { data } = await getPreferenceCommunicationChannelId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    