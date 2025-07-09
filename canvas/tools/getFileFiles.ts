
import { tool } from "ai";
import { getFileFilesDataSchema } from "./aitm.schema.ts";
import { getFileFiles, GetFileFilesData } from "..";

export default tool({
  description: `
  Get file
Returns the standard attachment json object
    `,
  parameters: getFileFilesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFileFilesData, "url"> ) => {
    try {
      const { data } = await getFileFiles(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    