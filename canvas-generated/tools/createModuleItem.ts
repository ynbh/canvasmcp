
import { tool } from "ai";
import { createModuleItemDataSchema } from "./aitm.schema.ts";
import { createModuleItem, CreateModuleItemData } from "..";

export default tool({
  description: `
  Create a module item
Create and return a new module item
    `,
  parameters: createModuleItemDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateModuleItemData, "url"> ) => {
    try {
      const { data } = await createModuleItem(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    