
import { tool } from "ai";
import { updateMigrationIssueAccountsDataSchema } from "./aitm.schema.ts";
import { updateMigrationIssueAccounts, UpdateMigrationIssueAccountsData } from "..";

export default tool({
  description: `
  Update a migration issue
Update the workflow_state of a migration issue
    `,
  parameters: updateMigrationIssueAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMigrationIssueAccountsData, "url"> ) => {
    try {
      const { data } = await updateMigrationIssueAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    