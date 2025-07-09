
import { tool } from "ai";
import { deleteCommunicationChannelTypeDataSchema } from "./aitm.schema.ts";
import { deleteCommunicationChannelType, DeleteCommunicationChannelTypeData } from "..";

export default tool({
  description: `
  Delete a communication channel
Delete an existing communication channel.
    `,
  parameters: deleteCommunicationChannelTypeDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteCommunicationChannelTypeData, "url"> ) => {
    try {
      const { data } = await deleteCommunicationChannelType(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    