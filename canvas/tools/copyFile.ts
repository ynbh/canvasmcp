
import { tool } from "ai";
import { copyFileDataSchema } from "./aitm.schema.ts";
import { copyFile, CopyFileData } from "..";

export default tool({
  description: `
  Copy a file
Copy a file from elsewhere in Canvas into a folder.

Copying a file across contexts
(between courses and users) is permitted,
but the source and destination must belong to the same
institution.
    `,
  parameters: copyFileDataSchema.omit({ url: true }),
  execute: async (args : Omit<CopyFileData, "url"> ) => {
    try {
      const { data } = await copyFile(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    