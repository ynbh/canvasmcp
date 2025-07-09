
import { tool } from "ai";
import { updateMigrationIssueUsersDataSchema } from "./aitm.schema.ts";
import { updateMigrationIssueUsers, UpdateMigrationIssueUsersData } from "..";

export default tool({
  description: `
  Update a migration issue
Update the workflow_state of a migration issue
    `,
  parameters: updateMigrationIssueUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMigrationIssueUsersData, "url"> ) => {
    try {
      const { data } = await updateMigrationIssueUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    