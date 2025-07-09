
import { tool } from "ai";
import { listMigrationSystemsCoursesDataSchema } from "./aitm.schema.ts";
import { listMigrationSystemsCourses, ListMigrationSystemsCoursesData } from "..";

export default tool({
  description: `
  List Migration Systems
Lists the currently available migration types. These values may change.
    `,
  parameters: listMigrationSystemsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMigrationSystemsCoursesData, "url"> ) => {
    try {
      const { data } = await listMigrationSystemsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    