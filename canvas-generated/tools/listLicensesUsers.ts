
import { tool } from "ai";
import { listLicensesUsersDataSchema } from "./aitm.schema.ts";
import { listLicensesUsers, ListLicensesUsersData } from "..";

export default tool({
  description: `
  List licenses
A paginated list of licenses that can be applied
    `,
  parameters: listLicensesUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLicensesUsersData, "url"> ) => {
    try {
      const { data } = await listLicensesUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    