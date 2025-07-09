
import { tool } from "ai";
import { listFilesFoldersDataSchema } from "./aitm.schema.ts";
import { listFilesFolders, ListFilesFoldersData } from "..";

export default tool({
  description: `
  List files
Returns the paginated list of files for the folder or course.
    `,
  parameters: listFilesFoldersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFilesFoldersData, "url"> ) => {
    try {
      const { data } = await listFilesFolders(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    