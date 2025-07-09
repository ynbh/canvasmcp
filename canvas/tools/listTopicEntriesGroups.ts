
import { tool } from "ai";
import { listTopicEntriesGroupsDataSchema } from "./aitm.schema.ts";
import { listTopicEntriesGroups, ListTopicEntriesGroupsData } from "..";

export default tool({
  description: `
  List topic entries
Retrieve the (paginated) top-level entries in a discussion topic.

May require
(depending on the topic) that the user has posted in the topic.
If it is required, and the user has
not posted, will respond with a 403
Forbidden status and the body 'require_initial_post'.

Will
include the 10 most recent replies, if any, for each entry returned.

If the topic is a root topic
with children corresponding to groups of a
group assignment, entries from those subtopics for which
the user belongs
to the corresponding group will be returned.

Ordering of returned entries is
newest-first by posting timestamp (reply
activity is ignored).
    `,
  parameters: listTopicEntriesGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListTopicEntriesGroupsData, "url"> ) => {
    try {
      const { data } = await listTopicEntriesGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    