
import { tool } from "ai";
import { deleteMessageDataSchema } from "./aitm.schema.ts";
import { deleteMessage, DeleteMessageData } from "..";

export default tool({
  description: `
  Delete a message
Delete messages from this conversation. Note that this only affects this
user's
view of the conversation. If all messages are deleted, the
conversation will be as well (equivalent
to DELETE)
    `,
  parameters: deleteMessageDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteMessageData, "url"> ) => {
    try {
      const { data } = await deleteMessage(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    