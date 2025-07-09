
import { tool } from "ai";
import { getFolderGroupsDataSchema } from "./aitm.schema.ts";
import { getFolderGroups, GetFolderGroupsData } from "..";

export default tool({
  description: `
  Get folder
Returns the details for a folder

You can get the root folder from a context by using
'root' as the :id.
For example, you could get the root folder for a course like:
    `,
  parameters: getFolderGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFolderGroupsData, "url"> ) => {
    try {
      const { data } = await getFolderGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    