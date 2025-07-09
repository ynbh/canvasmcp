
import { tool } from "ai";
import { reorderCustomColumnsDataSchema } from "./aitm.schema.ts";
import { reorderCustomColumns, ReorderCustomColumnsData } from "..";

export default tool({
  description: `
  Reorder custom columns
Puts the given columns in the specified order

<b>200 OK</b> is returned if
successful
    `,
  parameters: reorderCustomColumnsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReorderCustomColumnsData, "url"> ) => {
    try {
      const { data } = await reorderCustomColumns(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    