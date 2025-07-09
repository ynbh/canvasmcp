
import { tool } from "ai";
import { batchUpdateConversationsDataSchema } from "./aitm.schema.ts";
import { batchUpdateConversations, BatchUpdateConversationsData } from "..";

export default tool({
  description: `
  Batch update conversations
Perform a change on a set of conversations. Operates asynchronously; use
the {api:ProgressController#show progress endpoint}
to query the status of an operation.
    `,
  parameters: batchUpdateConversationsDataSchema.omit({ url: true }),
  execute: async (args : Omit<BatchUpdateConversationsData, "url"> ) => {
    try {
      const { data } = await batchUpdateConversations(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    