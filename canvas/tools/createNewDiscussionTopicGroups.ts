
import { tool } from "ai";
import { createNewDiscussionTopicGroupsDataSchema } from "./aitm.schema.ts";
import { createNewDiscussionTopicGroups, CreateNewDiscussionTopicGroupsData } from "..";

export default tool({
  description: `
  Create a new discussion topic
Create an new discussion topic for the course or group.
    `,
  parameters: createNewDiscussionTopicGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateNewDiscussionTopicGroupsData, "url"> ) => {
    try {
      const { data } = await createNewDiscussionTopicGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    