
import { tool } from "ai";
import { getContentMigrationGroupsDataSchema } from "./aitm.schema.ts";
import { getContentMigrationGroups, GetContentMigrationGroupsData } from "..";

export default tool({
  description: `
  Get a content migration
Returns data on an individual content migration
    `,
  parameters: getContentMigrationGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetContentMigrationGroupsData, "url"> ) => {
    try {
      const { data } = await getContentMigrationGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    