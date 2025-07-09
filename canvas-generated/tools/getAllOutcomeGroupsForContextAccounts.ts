
import { tool } from "ai";
import { getAllOutcomeGroupsForContextAccountsDataSchema } from "./aitm.schema.ts";
import { getAllOutcomeGroupsForContextAccounts, GetAllOutcomeGroupsForContextAccountsData } from "..";

export default tool({
  description: `
  Get all outcome groups for context
    `,
  parameters: getAllOutcomeGroupsForContextAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllOutcomeGroupsForContextAccountsData, "url"> ) => {
    try {
      const { data } = await getAllOutcomeGroupsForContextAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    