
import { tool } from "ai";
import { updateModuleItemDataSchema } from "./aitm.schema.ts";
import { updateModuleItem, UpdateModuleItemData } from "..";

export default tool({
  description: `
  Update a module item
Update and return an existing module item
    `,
  parameters: updateModuleItemDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateModuleItemData, "url"> ) => {
    try {
      const { data } = await updateModuleItem(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    