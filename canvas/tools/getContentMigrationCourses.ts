
import { tool } from "ai";
import { getContentMigrationCoursesDataSchema } from "./aitm.schema.ts";
import { getContentMigrationCourses, GetContentMigrationCoursesData } from "..";

export default tool({
  description: `
  Get a content migration
Returns data on an individual content migration
    `,
  parameters: getContentMigrationCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetContentMigrationCoursesData, "url"> ) => {
    try {
      const { data } = await getContentMigrationCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    