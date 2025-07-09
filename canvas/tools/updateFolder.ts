
import { tool } from "ai";
import { updateFolderDataSchema } from "./aitm.schema.ts";
import { updateFolder, UpdateFolderData } from "..";

export default tool({
  description: `
  Update folder
Updates a folder
    `,
  parameters: updateFolderDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateFolderData, "url"> ) => {
    try {
      const { data } = await updateFolder(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    