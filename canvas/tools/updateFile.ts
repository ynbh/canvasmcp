
import { tool } from "ai";
import { updateFileDataSchema } from "./aitm.schema.ts";
import { updateFile, UpdateFileData } from "..";

export default tool({
  description: `
  Update file
Update some settings on the specified file
    `,
  parameters: updateFileDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateFileData, "url"> ) => {
    try {
      const { data } = await updateFile(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    