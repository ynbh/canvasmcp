
import { tool } from "ai";
import { listAllFoldersGroupsDataSchema } from "./aitm.schema.ts";
import { listAllFoldersGroups, ListAllFoldersGroupsData } from "..";

export default tool({
  description: `
  List all folders
Returns the paginated list of all folders for the given context. This will
be
returned as a flat list containing all subfolders as well.
    `,
  parameters: listAllFoldersGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAllFoldersGroupsData, "url"> ) => {
    try {
      const { data } = await listAllFoldersGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    