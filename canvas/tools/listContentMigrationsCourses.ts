
import { tool } from "ai";
import { listContentMigrationsCoursesDataSchema } from "./aitm.schema.ts";
import { listContentMigrationsCourses, ListContentMigrationsCoursesData } from "..";

export default tool({
  description: `
  List content migrations
Returns paginated content migrations
    `,
  parameters: listContentMigrationsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListContentMigrationsCoursesData, "url"> ) => {
    try {
      const { data } = await listContentMigrationsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    