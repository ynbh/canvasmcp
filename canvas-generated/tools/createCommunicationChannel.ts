
import { tool } from "ai";
import { createCommunicationChannelDataSchema } from "./aitm.schema.ts";
import { createCommunicationChannel, CreateCommunicationChannelData } from "..";

export default tool({
  description: `
  Create a communication channel
Creates a new communication channel for the specified user.
    `,
  parameters: createCommunicationChannelDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateCommunicationChannelData, "url"> ) => {
    try {
      const { data } = await createCommunicationChannel(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    