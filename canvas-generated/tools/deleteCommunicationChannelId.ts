
import { tool } from "ai";
import { deleteCommunicationChannelIdDataSchema } from "./aitm.schema.ts";
import { deleteCommunicationChannelId, DeleteCommunicationChannelIdData } from "..";

export default tool({
  description: `
  Delete a communication channel
Delete an existing communication channel.
    `,
  parameters: deleteCommunicationChannelIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteCommunicationChannelIdData, "url"> ) => {
    try {
      const { data } = await deleteCommunicationChannelId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    