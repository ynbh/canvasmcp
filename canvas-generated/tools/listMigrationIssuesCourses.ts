
import { tool } from "ai";
import { listMigrationIssuesCoursesDataSchema } from "./aitm.schema.ts";
import { listMigrationIssuesCourses, ListMigrationIssuesCoursesData } from "..";

export default tool({
  description: `
  List migration issues
Returns paginated migration issues
    `,
  parameters: listMigrationIssuesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationIssuesCoursesData, "url"> ) => {
    try {
      const { data } = await listMigrationIssuesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    