
import { tool } from "ai";
import { markAllEntriesAsReadGroupsDataSchema } from "./aitm.schema.ts";
import { markAllEntriesAsReadGroups, MarkAllEntriesAsReadGroupsData } from "..";

export default tool({
  description: `
  Mark all entries as read
Mark the discussion topic and all its entries as read.

No request fields
are necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markAllEntriesAsReadGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkAllEntriesAsReadGroupsData, "url"> ) => {
    try {
      const { data } = await markAllEntriesAsReadGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    