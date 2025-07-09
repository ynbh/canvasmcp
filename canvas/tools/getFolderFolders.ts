
import { tool } from "ai";
import { getFolderFoldersDataSchema } from "./aitm.schema.ts";
import { getFolderFolders, GetFolderFoldersData } from "..";

export default tool({
  description: `
  Get folder
Returns the details for a folder

You can get the root folder from a context by using
'root' as the :id.
For example, you could get the root folder for a course like:
    `,
  parameters: getFolderFoldersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFolderFoldersData, "url"> ) => {
    try {
      const { data } = await getFolderFolders(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    