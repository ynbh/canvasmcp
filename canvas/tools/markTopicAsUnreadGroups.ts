
import { tool } from "ai";
import { markTopicAsUnreadGroupsDataSchema } from "./aitm.schema.ts";
import { markTopicAsUnreadGroups, MarkTopicAsUnreadGroupsData } from "..";

export default tool({
  description: `
  Mark topic as unread
Mark the initial text of the discussion topic as unread.

No request fields are
necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markTopicAsUnreadGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkTopicAsUnreadGroupsData, "url"> ) => {
    try {
      const { data } = await markTopicAsUnreadGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    