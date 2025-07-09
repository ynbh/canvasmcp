
import { tool } from "ai";
import { unsubscribeFromTopicGroupsDataSchema } from "./aitm.schema.ts";
import { unsubscribeFromTopicGroups, UnsubscribeFromTopicGroupsData } from "..";

export default tool({
  description: `
  Unsubscribe from a topic
Unsubscribe from a topic to stop receiving notifications about new
entries

On success, the response will be 204 No Content with an empty body
    `,
  parameters: unsubscribeFromTopicGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UnsubscribeFromTopicGroupsData, "url"> ) => {
    try {
      const { data } = await unsubscribeFromTopicGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    