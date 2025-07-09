
import { tool } from "ai";
import { deleteEntryGroupsDataSchema } from "./aitm.schema.ts";
import { deleteEntryGroups, DeleteEntryGroupsData } from "..";

export default tool({
  description: `
  Delete an entry
Delete a discussion entry.

The entry must have been created by the current user, or
the current user
must have admin rights to the discussion. If the delete is not allowed, a 401 will
be returned.

The discussion will be marked deleted, and the user_id and message will be cleared
out.
    `,
  parameters: deleteEntryGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteEntryGroupsData, "url"> ) => {
    try {
      const { data } = await deleteEntryGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    