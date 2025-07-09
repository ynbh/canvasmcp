
import { tool } from "ai";
import { deleteFolderDataSchema } from "./aitm.schema.ts";
import { deleteFolder, DeleteFolderData } from "..";

export default tool({
  description: `
  Delete folder
Remove the specified folder. You can only delete empty folders unless you
set the
'force' flag
    `,
  parameters: deleteFolderDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteFolderData, "url"> ) => {
    try {
      const { data } = await deleteFolder(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    