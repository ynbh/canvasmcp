
import { tool } from "ai";
import { showBlueprintImportDataSchema } from "./aitm.schema.ts";
import { showBlueprintImport, ShowBlueprintImportData } from "..";

export default tool({
  description: `
  Show a blueprint import
Shows the status of an import into a course associated with a blueprint. See
also
{api:MasterCourses::MasterTemplatesController#migrations_show the blueprint course side}.
    `,
  parameters: showBlueprintImportDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowBlueprintImportData, "url"> ) => {
    try {
      const { data } = await showBlueprintImport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    