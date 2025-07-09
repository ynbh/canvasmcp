
import { tool } from "ai";
import { listMigrationSystemsGroupsDataSchema } from "./aitm.schema.ts";
import { listMigrationSystemsGroups, ListMigrationSystemsGroupsData } from "..";

export default tool({
  description: `
  List Migration Systems
Lists the currently available migration types. These values may change.
    `,
  parameters: listMigrationSystemsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationSystemsGroupsData, "url"> ) => {
    try {
      const { data } = await listMigrationSystemsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    