
import { tool } from "ai";
import { hideAllStreamItemsDataSchema } from "./aitm.schema.ts";
import { hideAllStreamItems, HideAllStreamItemsData } from "..";

export default tool({
  description: `
  Hide all stream items
Hide all stream items for the user
    `,
  parameters: hideAllStreamItemsDataSchema.omit({ url: true }),
  execute: async (args : Omit<HideAllStreamItemsData, "url"> ) => {
    try {
      const { data } = await hideAllStreamItems(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    