
import { tool } from "ai";
import { deleteExternalFeedGroupsDataSchema } from "./aitm.schema.ts";
import { deleteExternalFeedGroups, DeleteExternalFeedGroupsData } from "..";

export default tool({
  description: `
  Delete an external feed
Deletes the external feed.
    `,
  parameters: deleteExternalFeedGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteExternalFeedGroupsData, "url"> ) => {
    try {
      const { data } = await deleteExternalFeedGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    