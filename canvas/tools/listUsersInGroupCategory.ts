
import { tool } from "ai";
import { listUsersInGroupCategoryDataSchema } from "./aitm.schema.ts";
import { listUsersInGroupCategory, ListUsersInGroupCategoryData } from "..";

export default tool({
  description: `
  List users in group category
Returns a paginated list of users in the group category.
    `,
  parameters: listUsersInGroupCategoryDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUsersInGroupCategoryData, "url"> ) => {
    try {
      const { data } = await listUsersInGroupCategory(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    