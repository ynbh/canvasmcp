
import { tool } from "ai";
import { updateMigrationIssueCoursesDataSchema } from "./aitm.schema.ts";
import { updateMigrationIssueCourses, UpdateMigrationIssueCoursesData } from "..";

export default tool({
  description: `
  Update a migration issue
Update the workflow_state of a migration issue
    `,
  parameters: updateMigrationIssueCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMigrationIssueCoursesData, "url"> ) => {
    try {
      const { data } = await updateMigrationIssueCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    