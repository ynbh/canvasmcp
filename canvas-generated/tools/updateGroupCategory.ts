
import { tool } from "ai";
import { updateGroupCategoryDataSchema } from "./aitm.schema.ts";
import { updateGroupCategory, UpdateGroupCategoryData } from "..";

export default tool({
  description: `
  Update a Group Category
Modifies an existing group category.
    `,
  parameters: updateGroupCategoryDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateGroupCategoryData, "url"> ) => {
    try {
      const { data } = await updateGroupCategory(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    