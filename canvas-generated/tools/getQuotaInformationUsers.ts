
import { tool } from "ai";
import { getQuotaInformationUsersDataSchema } from "./aitm.schema.ts";
import { getQuotaInformationUsers, GetQuotaInformationUsersData } from "..";

export default tool({
  description: `
  Get quota information
Returns the total and used storage quota for the course, group, or user.
    `,
  parameters: getQuotaInformationUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetQuotaInformationUsersData, "url"> ) => {
    try {
      const { data } = await getQuotaInformationUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    