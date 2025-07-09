
import { tool } from "ai";
import { listFoldersDataSchema } from "./aitm.schema.ts";
import { listFolders, ListFoldersData } from "..";

export default tool({
  description: `
  List folders
Returns the paginated list of folders in the folder.
    `,
  parameters: listFoldersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFoldersData, "url"> ) => {
    try {
      const { data } = await listFolders(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    