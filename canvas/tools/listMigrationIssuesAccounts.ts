
import { tool } from "ai";
import { listMigrationIssuesAccountsDataSchema } from "./aitm.schema.ts";
import { listMigrationIssuesAccounts, ListMigrationIssuesAccountsData } from "..";

export default tool({
  description: `
  List migration issues
Returns paginated migration issues
    `,
  parameters: listMigrationIssuesAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationIssuesAccountsData, "url"> ) => {
    try {
      const { data } = await listMigrationIssuesAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    