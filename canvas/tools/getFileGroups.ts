
import { tool } from "ai";
import { getFileGroupsDataSchema } from "./aitm.schema.ts";
import { getFileGroups, GetFileGroupsData } from "..";

export default tool({
  description: `
  Get file
Returns the standard attachment json object
    `,
  parameters: getFileGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFileGroupsData, "url"> ) => {
    try {
      const { data } = await getFileGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    