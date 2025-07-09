
import { tool } from "ai";
import { getSingleTopicGroupsDataSchema } from "./aitm.schema.ts";
import { getSingleTopicGroups, GetSingleTopicGroupsData } from "..";

export default tool({
  description: `
  Get a single topic
Returns data on an individual discussion topic. See the List action for the
response formatting.
    `,
  parameters: getSingleTopicGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleTopicGroupsData, "url"> ) => {
    try {
      const { data } = await getSingleTopicGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    