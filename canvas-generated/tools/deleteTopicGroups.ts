
import { tool } from "ai";
import { deleteTopicGroupsDataSchema } from "./aitm.schema.ts";
import { deleteTopicGroups, DeleteTopicGroupsData } from "..";

export default tool({
  description: `
  Delete a topic
Deletes the discussion topic. This will also delete the assignment, if it's
an
assignment discussion.
    `,
  parameters: deleteTopicGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteTopicGroupsData, "url"> ) => {
    try {
      const { data } = await deleteTopicGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    