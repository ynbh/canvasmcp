
import { tool } from "ai";
import { getMigrationIssueGroupsDataSchema } from "./aitm.schema.ts";
import { getMigrationIssueGroups, GetMigrationIssueGroupsData } from "..";

export default tool({
  description: `
  Get a migration issue
Returns data on an individual migration issue
    `,
  parameters: getMigrationIssueGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetMigrationIssueGroupsData, "url"> ) => {
    try {
      const { data } = await getMigrationIssueGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    