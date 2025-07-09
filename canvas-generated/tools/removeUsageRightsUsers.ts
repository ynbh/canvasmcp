
import { tool } from "ai";
import { removeUsageRightsUsersDataSchema } from "./aitm.schema.ts";
import { removeUsageRightsUsers, RemoveUsageRightsUsersData } from "..";

export default tool({
  description: `
  Remove usage rights
Removes copyright and license information associated with one or more files
    `,
  parameters: removeUsageRightsUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveUsageRightsUsersData, "url"> ) => {
    try {
      const { data } = await removeUsageRightsUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    