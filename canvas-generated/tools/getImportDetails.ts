
import { tool } from "ai";
import { getImportDetailsDataSchema } from "./aitm.schema.ts";
import { getImportDetails, GetImportDetailsData } from "..";

export default tool({
  description: `
  Get import details
Show the changes that were propagated to a course associated with a blueprint.
See also
{api:MasterCourses::MasterTemplatesController#migration_details the blueprint course side}.
    `,
  parameters: getImportDetailsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetImportDetailsData, "url"> ) => {
    try {
      const { data } = await getImportDetails(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    