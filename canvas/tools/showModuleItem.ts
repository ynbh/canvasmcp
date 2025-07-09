
import { tool } from "ai";
import { showModuleItemDataSchema } from "./aitm.schema.ts";
import { showModuleItem, ShowModuleItemData } from "..";

export default tool({
  description: `
  Show module item
Get information about a single module item
    `,
  parameters: showModuleItemDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowModuleItemData, "url"> ) => {
    try {
      const { data } = await showModuleItem(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    