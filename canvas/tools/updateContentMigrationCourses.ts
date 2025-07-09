
import { tool } from "ai";
import { updateContentMigrationCoursesDataSchema } from "./aitm.schema.ts";
import { updateContentMigrationCourses, UpdateContentMigrationCoursesData } from "..";

export default tool({
  description: `
  Update a content migration
Update a content migration. Takes same arguments as create except that
you
can't change the migration type. However, changing most settings after the
migration process has
started will not do anything. Generally updating the
content migration will be used when there is a
file upload problem. If the
first upload has a problem you can supply new _pre_attachment_ values
to
start the process again.
    `,
  parameters: updateContentMigrationCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateContentMigrationCoursesData, "url"> ) => {
    try {
      const { data } = await updateContentMigrationCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    