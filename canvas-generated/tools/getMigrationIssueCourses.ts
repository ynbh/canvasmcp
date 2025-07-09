
import { tool } from "ai";
import { getMigrationIssueCoursesDataSchema } from "./aitm.schema.ts";
import { getMigrationIssueCourses, GetMigrationIssueCoursesData } from "..";

export default tool({
  description: `
  Get a migration issue
Returns data on an individual migration issue
    `,
  parameters: getMigrationIssueCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetMigrationIssueCoursesData, "url"> ) => {
    try {
      const { data } = await getMigrationIssueCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    