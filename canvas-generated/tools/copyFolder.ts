
import { tool } from "ai";
import { copyFolderDataSchema } from "./aitm.schema.ts";
import { copyFolder, CopyFolderData } from "..";

export default tool({
  description: `
  Copy a folder
Copy a folder (and its contents) from elsewhere in Canvas into a folder.

Copying a
folder across contexts (between courses and users) is permitted,
but the source and destination must
belong to the same institution.
If the source and destination folders are in the same context,
the
source folder may not contain the destination folder. A folder will be
renamed at its
destination if another folder with the same name already
exists.
    `,
  parameters: copyFolderDataSchema.omit({ url: true }),
  execute: async (args : Omit<CopyFolderData, "url"> ) => {
    try {
      const { data } = await copyFolder(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    