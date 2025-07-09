
import { tool } from "ai";
import { markEntryAsUnreadGroupsDataSchema } from "./aitm.schema.ts";
import { markEntryAsUnreadGroups, MarkEntryAsUnreadGroupsData } from "..";

export default tool({
  description: `
  Mark entry as unread
Mark a discussion entry as unread.

No request fields are necessary.

On
success, the response will be 204 No Content with an empty body.
    `,
  parameters: markEntryAsUnreadGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkEntryAsUnreadGroupsData, "url"> ) => {
    try {
      const { data } = await markEntryAsUnreadGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    