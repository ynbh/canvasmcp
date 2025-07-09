
import { tool } from "ai";
import { getFolderUsersDataSchema } from "./aitm.schema.ts";
import { getFolderUsers, GetFolderUsersData } from "..";

export default tool({
  description: `
  Get folder
Returns the details for a folder

You can get the root folder from a context by using
'root' as the :id.
For example, you could get the root folder for a course like:
    `,
  parameters: getFolderUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFolderUsersData, "url"> ) => {
    try {
      const { data } = await getFolderUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    