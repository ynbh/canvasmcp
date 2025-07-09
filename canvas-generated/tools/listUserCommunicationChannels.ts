
import { tool } from "ai";
import { listUserCommunicationChannelsDataSchema } from "./aitm.schema.ts";
import { listUserCommunicationChannels, ListUserCommunicationChannelsData } from "..";

export default tool({
  description: `
  List user communication channels
Returns a paginated list of communication channels for the
specified user,
sorted by position.
    `,
  parameters: listUserCommunicationChannelsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUserCommunicationChannelsData, "url"> ) => {
    try {
      const { data } = await listUserCommunicationChannels(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    