
import { tool } from "ai";
import { listBlueprintMigrationsDataSchema } from "./aitm.schema.ts";
import { listBlueprintMigrations, ListBlueprintMigrationsData } from "..";

export default tool({
  description: `
  List blueprint migrations
Shows a paginated list of migrations for the template, starting with the
most recent. This endpoint can be called on a
blueprint course. See also
{api:MasterCourses::MasterTemplatesController#imports_index the associated course side}.
    `,
  parameters: listBlueprintMigrationsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListBlueprintMigrationsData, "url"> ) => {
    try {
      const { data } = await listBlueprintMigrations(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    