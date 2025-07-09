
import { tool } from "ai";
import { updateContentMigrationGroupsDataSchema } from "./aitm.schema.ts";
import { updateContentMigrationGroups, UpdateContentMigrationGroupsData } from "..";

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
  parameters: updateContentMigrationGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateContentMigrationGroupsData, "url"> ) => {
    try {
      const { data } = await updateContentMigrationGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    