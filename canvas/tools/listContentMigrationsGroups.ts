
import { tool } from "ai";
import { listContentMigrationsGroupsDataSchema } from "./aitm.schema.ts";
import { listContentMigrationsGroups, ListContentMigrationsGroupsData } from "..";

export default tool({
  description: `
  List content migrations
Returns paginated content migrations
    `,
  parameters: listContentMigrationsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListContentMigrationsGroupsData, "url"> ) => {
    try {
      const { data } = await listContentMigrationsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    