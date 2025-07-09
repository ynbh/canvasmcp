
import { tool } from "ai";
import { markEntryAsReadGroupsDataSchema } from "./aitm.schema.ts";
import { markEntryAsReadGroups, MarkEntryAsReadGroupsData } from "..";

export default tool({
  description: `
  Mark entry as read
Mark a discussion entry as read.

No request fields are necessary.

On success,
the response will be 204 No Content with an empty body.
    `,
  parameters: markEntryAsReadGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkEntryAsReadGroupsData, "url"> ) => {
    try {
      const { data } = await markEntryAsReadGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    