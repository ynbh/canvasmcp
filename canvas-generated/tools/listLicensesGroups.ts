
import { tool } from "ai";
import { listLicensesGroupsDataSchema } from "./aitm.schema.ts";
import { listLicensesGroups, ListLicensesGroupsData } from "..";

export default tool({
  description: `
  List licenses
A paginated list of licenses that can be applied
    `,
  parameters: listLicensesGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLicensesGroupsData, "url"> ) => {
    try {
      const { data } = await listLicensesGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    