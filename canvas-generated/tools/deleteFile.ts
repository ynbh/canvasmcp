
import { tool } from "ai";
import { deleteFileDataSchema } from "./aitm.schema.ts";
import { deleteFile, DeleteFileData } from "..";

export default tool({
  description: `
  Delete file
Remove the specified file
    `,
  parameters: deleteFileDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteFileData, "url"> ) => {
    try {
      const { data } = await deleteFile(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    