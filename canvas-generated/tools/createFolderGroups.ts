
import { tool } from "ai";
import { createFolderGroupsDataSchema } from "./aitm.schema.ts";
import { createFolderGroups, CreateFolderGroupsData } from "..";

export default tool({
  description: `
  Create folder
Creates a folder in the specified context
    `,
  parameters: createFolderGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateFolderGroupsData, "url"> ) => {
    try {
      const { data } = await createFolderGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    