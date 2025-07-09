
import { tool } from "ai";
import { createFolderFoldersDataSchema } from "./aitm.schema.ts";
import { createFolderFolders, CreateFolderFoldersData } from "..";

export default tool({
  description: `
  Create folder
Creates a folder in the specified context
    `,
  parameters: createFolderFoldersDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateFolderFoldersData, "url"> ) => {
    try {
      const { data } = await createFolderFolders(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    