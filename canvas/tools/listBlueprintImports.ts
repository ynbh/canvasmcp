
import { tool } from "ai";
import { listBlueprintImportsDataSchema } from "./aitm.schema.ts";
import { listBlueprintImports, ListBlueprintImportsData } from "..";

export default tool({
  description: `
  List blueprint imports
Shows a paginated list of migrations imported into a course associated with a
blueprint, starting with the most recent. See
also
{api:MasterCourses::MasterTemplatesController#migrations_index the blueprint course side}.

Use
'default' as the subscription_id to use the currently active blueprint subscription.
    `,
  parameters: listBlueprintImportsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListBlueprintImportsData, "url"> ) => {
    try {
      const { data } = await listBlueprintImports(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    