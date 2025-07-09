
import { tool } from "ai";
import { setUsageRightsUsersDataSchema } from "./aitm.schema.ts";
import { setUsageRightsUsers, SetUsageRightsUsersData } from "..";

export default tool({
  description: `
  Set usage rights
Sets copyright and license information for one or more files
    `,
  parameters: setUsageRightsUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetUsageRightsUsersData, "url"> ) => {
    try {
      const { data } = await setUsageRightsUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    