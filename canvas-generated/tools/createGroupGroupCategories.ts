
import { tool } from "ai";
import { createGroupGroupCategoriesDataSchema } from "./aitm.schema.ts";
import { createGroupGroupCategories, CreateGroupGroupCategoriesData } from "..";

export default tool({
  description: `
  Create a group
Creates a new group. Groups created using the "/api/v1/groups/"
endpoint will be
community groups.
    `,
  parameters: createGroupGroupCategoriesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateGroupGroupCategoriesData, "url"> ) => {
    try {
      const { data } = await createGroupGroupCategories(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    