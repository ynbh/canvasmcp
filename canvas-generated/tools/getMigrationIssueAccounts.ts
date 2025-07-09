
import { tool } from "ai";
import { getMigrationIssueAccountsDataSchema } from "./aitm.schema.ts";
import { getMigrationIssueAccounts, GetMigrationIssueAccountsData } from "..";

export default tool({
  description: `
  Get a migration issue
Returns data on an individual migration issue
    `,
  parameters: getMigrationIssueAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetMigrationIssueAccountsData, "url"> ) => {
    try {
      const { data } = await getMigrationIssueAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    