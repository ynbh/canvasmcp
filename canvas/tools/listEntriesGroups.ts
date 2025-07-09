
import { tool } from "ai";
import { listEntriesGroupsDataSchema } from "./aitm.schema.ts";
import { listEntriesGroups, ListEntriesGroupsData } from "..";

export default tool({
  description: `
  List entries
Retrieve a paginated list of discussion entries, given a list of ids.

May require
(depending on the topic) that the user has posted in the topic.
If it is required, and the user has
not posted, will respond with a 403
Forbidden status and the body 'require_initial_post'.
    `,
  parameters: listEntriesGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEntriesGroupsData, "url"> ) => {
    try {
      const { data } = await listEntriesGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    