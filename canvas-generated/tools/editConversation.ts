
import { tool } from "ai";
import { editConversationDataSchema } from "./aitm.schema.ts";
import { editConversation, EditConversationData } from "..";

export default tool({
  description: `
  Edit a conversation
Updates attributes for a single conversation.
    `,
  parameters: editConversationDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditConversationData, "url"> ) => {
    try {
      const { data } = await editConversation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    