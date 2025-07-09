
import { tool } from "ai";
import { subscribeToTopicGroupsDataSchema } from "./aitm.schema.ts";
import { subscribeToTopicGroups, SubscribeToTopicGroupsData } from "..";

export default tool({
  description: `
  Subscribe to a topic
Subscribe to a topic to receive notifications about new entries

On success,
the response will be 204 No Content with an empty body
    `,
  parameters: subscribeToTopicGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<SubscribeToTopicGroupsData, "url"> ) => {
    try {
      const { data } = await subscribeToTopicGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    