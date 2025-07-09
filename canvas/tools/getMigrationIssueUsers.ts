
import { tool } from "ai";
import { getMigrationIssueUsersDataSchema } from "./aitm.schema.ts";
import { getMigrationIssueUsers, GetMigrationIssueUsersData } from "..";

export default tool({
  description: `
  Get a migration issue
Returns data on an individual migration issue
    `,
  parameters: getMigrationIssueUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetMigrationIssueUsersData, "url"> ) => {
    try {
      const { data } = await getMigrationIssueUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    