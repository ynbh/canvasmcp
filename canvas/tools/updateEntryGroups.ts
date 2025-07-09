
import { tool } from "ai";
import { updateEntryGroupsDataSchema } from "./aitm.schema.ts";
import { updateEntryGroups, UpdateEntryGroupsData } from "..";

export default tool({
  description: `
  Update an entry
Update an existing discussion entry.

The entry must have been created by the
current user, or the current user
must have admin rights to the discussion. If the edit is not
allowed, a 401 will be returned.
    `,
  parameters: updateEntryGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateEntryGroupsData, "url"> ) => {
    try {
      const { data } = await updateEntryGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    