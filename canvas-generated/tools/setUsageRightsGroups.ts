
import { tool } from "ai";
import { setUsageRightsGroupsDataSchema } from "./aitm.schema.ts";
import { setUsageRightsGroups, SetUsageRightsGroupsData } from "..";

export default tool({
  description: `
  Set usage rights
Sets copyright and license information for one or more files
    `,
  parameters: setUsageRightsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetUsageRightsGroupsData, "url"> ) => {
    try {
      const { data } = await setUsageRightsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    