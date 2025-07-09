
import { tool } from "ai";
import { createFolderUsersDataSchema } from "./aitm.schema.ts";
import { createFolderUsers, CreateFolderUsersData } from "..";

export default tool({
  description: `
  Create folder
Creates a folder in the specified context
    `,
  parameters: createFolderUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateFolderUsersData, "url"> ) => {
    try {
      const { data } = await createFolderUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    