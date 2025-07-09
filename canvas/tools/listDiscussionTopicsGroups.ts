
import { tool } from "ai";
import { listDiscussionTopicsGroupsDataSchema } from "./aitm.schema.ts";
import { listDiscussionTopicsGroups, ListDiscussionTopicsGroupsData } from "..";

export default tool({
  description: `
  List discussion topics
Returns the paginated list of discussion topics for this course or group.
    `,
  parameters: listDiscussionTopicsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListDiscussionTopicsGroupsData, "url"> ) => {
    try {
      const { data } = await listDiscussionTopicsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    