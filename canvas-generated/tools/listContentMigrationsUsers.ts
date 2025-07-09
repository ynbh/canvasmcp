
import { tool } from "ai";
import { listContentMigrationsUsersDataSchema } from "./aitm.schema.ts";
import { listContentMigrationsUsers, ListContentMigrationsUsersData } from "..";

export default tool({
  description: `
  List content migrations
Returns paginated content migrations
    `,
  parameters: listContentMigrationsUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListContentMigrationsUsersData, "url"> ) => {
    try {
      const { data } = await listContentMigrationsUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    