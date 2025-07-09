
import { tool } from "ai";
import { listEntryRepliesGroupsDataSchema } from "./aitm.schema.ts";
import { listEntryRepliesGroups, ListEntryRepliesGroupsData } from "..";

export default tool({
  description: `
  List entry replies
Retrieve the (paginated) replies to a top-level entry in a discussion
topic.

May
require (depending on the topic) that the user has posted in the topic.
If it is required, and the
user has not posted, will respond with a 403
Forbidden status and the body
'require_initial_post'.

Ordering of returned entries is newest-first by creation timestamp.
    `,
  parameters: listEntryRepliesGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEntryRepliesGroupsData, "url"> ) => {
    try {
      const { data } = await listEntryRepliesGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    