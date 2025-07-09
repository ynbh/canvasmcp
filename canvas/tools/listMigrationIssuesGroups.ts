
import { tool } from "ai";
import { listMigrationIssuesGroupsDataSchema } from "./aitm.schema.ts";
import { listMigrationIssuesGroups, ListMigrationIssuesGroupsData } from "..";

export default tool({
  description: `
  List migration issues
Returns paginated migration issues
    `,
  parameters: listMigrationIssuesGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationIssuesGroupsData, "url"> ) => {
    try {
      const { data } = await listMigrationIssuesGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    