
import { tool } from "ai";
import { createConversationDataSchema } from "./aitm.schema.ts";
import { createConversation, CreateConversationData } from "..";

export default tool({
  description: `
  Create a conversation
Create a new conversation with one or more recipients. If there is already
an
existing private conversation with the given recipients, it will be
reused.
    `,
  parameters: createConversationDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateConversationData, "url"> ) => {
    try {
      const { data } = await createConversation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    