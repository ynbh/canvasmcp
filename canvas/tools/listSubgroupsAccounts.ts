
import { tool } from "ai";
import { listSubgroupsAccountsDataSchema } from "./aitm.schema.ts";
import { listSubgroupsAccounts, ListSubgroupsAccountsData } from "..";

export default tool({
  description: `
  List subgroups
A paginated list of the immediate OutcomeGroup children of the outcome group.
    `,
  parameters: listSubgroupsAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListSubgroupsAccountsData, "url"> ) => {
    try {
      const { data } = await listSubgroupsAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    