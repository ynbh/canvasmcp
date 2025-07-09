
import { tool } from "ai";
import { hideStreamItemDataSchema } from "./aitm.schema.ts";
import { hideStreamItem, HideStreamItemData } from "..";

export default tool({
  description: `
  Hide a stream item
Hide the given stream item.
    `,
  parameters: hideStreamItemDataSchema.omit({ url: true }),
  execute: async (args : Omit<HideStreamItemData, "url"> ) => {
    try {
      const { data } = await hideStreamItem(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    