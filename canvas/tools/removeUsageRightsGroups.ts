
import { tool } from "ai";
import { removeUsageRightsGroupsDataSchema } from "./aitm.schema.ts";
import { removeUsageRightsGroups, RemoveUsageRightsGroupsData } from "..";

export default tool({
  description: `
  Remove usage rights
Removes copyright and license information associated with one or more files
    `,
  parameters: removeUsageRightsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveUsageRightsGroupsData, "url"> ) => {
    try {
      const { data } = await removeUsageRightsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    