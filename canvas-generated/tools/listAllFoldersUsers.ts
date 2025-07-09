
import { tool } from "ai";
import { listAllFoldersUsersDataSchema } from "./aitm.schema.ts";
import { listAllFoldersUsers, ListAllFoldersUsersData } from "..";

export default tool({
  description: `
  List all folders
Returns the paginated list of all folders for the given context. This will
be
returned as a flat list containing all subfolders as well.
    `,
  parameters: listAllFoldersUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAllFoldersUsersData, "url"> ) => {
    try {
      const { data } = await listAllFoldersUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    