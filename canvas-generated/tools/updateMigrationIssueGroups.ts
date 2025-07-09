
import { tool } from "ai";
import { updateMigrationIssueGroupsDataSchema } from "./aitm.schema.ts";
import { updateMigrationIssueGroups, UpdateMigrationIssueGroupsData } from "..";

export default tool({
  description: `
  Update a migration issue
Update the workflow_state of a migration issue
    `,
  parameters: updateMigrationIssueGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMigrationIssueGroupsData, "url"> ) => {
    try {
      const { data } = await updateMigrationIssueGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    