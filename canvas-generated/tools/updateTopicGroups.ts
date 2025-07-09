
import { tool } from "ai";
import { updateTopicGroupsDataSchema } from "./aitm.schema.ts";
import { updateTopicGroups, UpdateTopicGroupsData } from "..";

export default tool({
  description: `
  Update a topic
Update an existing discussion topic for the course or group.
    `,
  parameters: updateTopicGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateTopicGroupsData, "url"> ) => {
    try {
      const { data } = await updateTopicGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    