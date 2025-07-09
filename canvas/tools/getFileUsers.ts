
import { tool } from "ai";
import { getFileUsersDataSchema } from "./aitm.schema.ts";
import { getFileUsers, GetFileUsersData } from "..";

export default tool({
  description: `
  Get file
Returns the standard attachment json object
    `,
  parameters: getFileUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFileUsersData, "url"> ) => {
    try {
      const { data } = await getFileUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    