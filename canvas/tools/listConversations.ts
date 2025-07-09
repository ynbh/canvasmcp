
import { tool } from "ai";
import { listConversationsDataSchema } from "./aitm.schema.ts";
import { listConversations, ListConversationsData } from "..";

export default tool({
  description: `
  List conversations
Returns the paginated list of conversations for the current user, most
recent
ones first.
    `,
  parameters: listConversationsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListConversationsData, "url"> ) => {
    try {
      const { data } = await listConversations(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    