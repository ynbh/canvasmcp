
import { tool } from "ai";
import { listMigrationSystemsAccountsDataSchema } from "./aitm.schema.ts";
import { listMigrationSystemsAccounts, ListMigrationSystemsAccountsData } from "..";

export default tool({
  description: `
  List Migration Systems
Lists the currently available migration types. These values may change.
    `,
  parameters: listMigrationSystemsAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationSystemsAccountsData, "url"> ) => {
    try {
      const { data } = await listMigrationSystemsAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    