
import { tool } from "ai";
import { listMigrationSystemsUsersDataSchema } from "./aitm.schema.ts";
import { listMigrationSystemsUsers, ListMigrationSystemsUsersData } from "..";

export default tool({
  description: `
  List Migration Systems
Lists the currently available migration types. These values may change.
    `,
  parameters: listMigrationSystemsUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationSystemsUsersData, "url"> ) => {
    try {
      const { data } = await listMigrationSystemsUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    