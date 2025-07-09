
import { tool } from "ai";
import { getMigrationDetailsDataSchema } from "./aitm.schema.ts";
import { getMigrationDetails, GetMigrationDetailsData } from "..";

export default tool({
  description: `
  Get migration details
Show the changes that were propagated in a blueprint migration. This endpoint
can be called on a
blueprint course. See also
{api:MasterCourses::MasterTemplatesController#import_details the associated course side}.
    `,
  parameters: getMigrationDetailsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetMigrationDetailsData, "url"> ) => {
    try {
      const { data } = await getMigrationDetails(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    