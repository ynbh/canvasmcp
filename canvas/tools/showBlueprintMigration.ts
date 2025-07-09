
import { tool } from "ai";
import { showBlueprintMigrationDataSchema } from "./aitm.schema.ts";
import { showBlueprintMigration, ShowBlueprintMigrationData } from "..";

export default tool({
  description: `
  Show a blueprint migration
Shows the status of a migration. This endpoint can be called on a
blueprint course. See also
{api:MasterCourses::MasterTemplatesController#imports_show the associated
course side}.
    `,
  parameters: showBlueprintMigrationDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowBlueprintMigrationData, "url"> ) => {
    try {
      const { data } = await showBlueprintMigration(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    