
import { tool } from "ai";
import { listContentMigrationsAccountsDataSchema } from "./aitm.schema.ts";
import { listContentMigrationsAccounts, ListContentMigrationsAccountsData } from "..";

export default tool({
  description: `
  List content migrations
Returns paginated content migrations
    `,
  parameters: listContentMigrationsAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListContentMigrationsAccountsData, "url"> ) => {
    try {
      const { data } = await listContentMigrationsAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    