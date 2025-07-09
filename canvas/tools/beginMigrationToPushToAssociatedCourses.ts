
import { tool } from "ai";
import { beginMigrationToPushToAssociatedCoursesDataSchema } from "./aitm.schema.ts";
import { beginMigrationToPushToAssociatedCourses, BeginMigrationToPushToAssociatedCoursesData } from "..";

export default tool({
  description: `
  Begin a migration to push to associated courses
Begins a migration to push recently updated content
to all associated courses.
Only one migration can be running at a time.
    `,
  parameters: beginMigrationToPushToAssociatedCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<BeginMigrationToPushToAssociatedCoursesData, "url"> ) => {
    try {
      const { data } = await beginMigrationToPushToAssociatedCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    