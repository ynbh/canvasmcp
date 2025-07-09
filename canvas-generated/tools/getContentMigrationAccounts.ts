
import { tool } from "ai";
import { getContentMigrationAccountsDataSchema } from "./aitm.schema.ts";
import { getContentMigrationAccounts, GetContentMigrationAccountsData } from "..";

export default tool({
  description: `
  Get a content migration
Returns data on an individual content migration
    `,
  parameters: getContentMigrationAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetContentMigrationAccountsData, "url"> ) => {
    try {
      const { data } = await getContentMigrationAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    