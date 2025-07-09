
import { tool } from "ai";
import { deleteModuleItemDataSchema } from "./aitm.schema.ts";
import { deleteModuleItem, DeleteModuleItemData } from "..";

export default tool({
  description: `
  Delete module item
Delete a module item
    `,
  parameters: deleteModuleItemDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteModuleItemData, "url"> ) => {
    try {
      const { data } = await deleteModuleItem(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    