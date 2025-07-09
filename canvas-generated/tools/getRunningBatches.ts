
import { tool } from "ai";
import { getRunningBatchesDataSchema } from "./aitm.schema.ts";
import { getRunningBatches, GetRunningBatchesData } from "..";

export default tool({
  description: `
  Get running batches
Returns any currently running conversation batches for the current
user.
Conversation batches are created when a bulk private message is sent
asynchronously (see the
mode argument to the {api:ConversationsController#create create API action}).
    `,
  parameters: getRunningBatchesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetRunningBatchesData, "url"> ) => {
    try {
      const { data } = await getRunningBatches(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    