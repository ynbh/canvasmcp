
import { tool } from "ai";
import { deleteGroupCategoryDataSchema } from "./aitm.schema.ts";
import { deleteGroupCategory, DeleteGroupCategoryData } from "..";

export default tool({
  description: `
  Delete a Group Category
Deletes a group category and all groups under it. Protected group
categories
can not be deleted, i.e. "communities" and "student_organized".
    `,
  parameters: deleteGroupCategoryDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteGroupCategoryData, "url"> ) => {
    try {
      const { data } = await deleteGroupCategory(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    