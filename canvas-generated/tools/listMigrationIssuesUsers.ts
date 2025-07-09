
import { tool } from "ai";
import { listMigrationIssuesUsersDataSchema } from "./aitm.schema.ts";
import { listMigrationIssuesUsers, ListMigrationIssuesUsersData } from "..";

export default tool({
  description: `
  List migration issues
Returns paginated migration issues
    `,
  parameters: listMigrationIssuesUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationIssuesUsersData, "url"> ) => {
    try {
      const { data } = await listMigrationIssuesUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    