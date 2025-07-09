
import { tool } from "ai";
import { deleteConversationDataSchema } from "./aitm.schema.ts";
import { deleteConversation, DeleteConversationData } from "..";

export default tool({
  description: `
  Delete a conversation
Delete this conversation and its messages. Note that this only deletes
this
user's view of the conversation.

Response includes same fields as UPDATE action
    `,
  parameters: deleteConversationDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteConversationData, "url"> ) => {
    try {
      const { data } = await deleteConversation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    