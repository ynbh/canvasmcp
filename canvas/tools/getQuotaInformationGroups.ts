
import { tool } from "ai";
import { getQuotaInformationGroupsDataSchema } from "./aitm.schema.ts";
import { getQuotaInformationGroups, GetQuotaInformationGroupsData } from "..";

export default tool({
  description: `
  Get quota information
Returns the total and used storage quota for the course, group, or user.
    `,
  parameters: getQuotaInformationGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetQuotaInformationGroupsData, "url"> ) => {
    try {
      const { data } = await getQuotaInformationGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    