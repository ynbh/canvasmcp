
import { tool } from "ai";
import { listModuleItemsDataSchema } from "./aitm.schema.ts";
import { listModuleItems, ListModuleItemsData } from "..";

export default tool({
  description: `
  List module items
A paginated list of the items in a module
    `,
  parameters: listModuleItemsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListModuleItemsData, "url"> ) => {
    try {
      const { data } = await listModuleItems(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    