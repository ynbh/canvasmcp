
import { tool } from "ai";
import { listEntriesForColumnDataSchema } from "./aitm.schema.ts";
import { listEntriesForColumn, ListEntriesForColumnData } from "..";

export default tool({
  description: `
  List entries for a column
This does not list entries for students without associated data.
    `,
  parameters: listEntriesForColumnDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEntriesForColumnData, "url"> ) => {
    try {
      const { data } = await listEntriesForColumn(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    