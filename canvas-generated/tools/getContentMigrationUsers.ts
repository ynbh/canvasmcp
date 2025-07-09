
import { tool } from "ai";
import { getContentMigrationUsersDataSchema } from "./aitm.schema.ts";
import { getContentMigrationUsers, GetContentMigrationUsersData } from "..";

export default tool({
  description: `
  Get a content migration
Returns data on an individual content migration
    `,
  parameters: getContentMigrationUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetContentMigrationUsersData, "url"> ) => {
    try {
      const { data } = await getContentMigrationUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    