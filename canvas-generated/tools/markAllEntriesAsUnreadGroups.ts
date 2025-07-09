
import { tool } from "ai";
import { markAllEntriesAsUnreadGroupsDataSchema } from "./aitm.schema.ts";
import { markAllEntriesAsUnreadGroups, MarkAllEntriesAsUnreadGroupsData } from "..";

export default tool({
  description: `
  Mark all entries as unread
Mark the discussion topic and all its entries as unread.

No request
fields are necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markAllEntriesAsUnreadGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkAllEntriesAsUnreadGroupsData, "url"> ) => {
    try {
      const { data } = await markAllEntriesAsUnreadGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    