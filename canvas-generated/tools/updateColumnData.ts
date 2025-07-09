
import { tool } from "ai";
import { updateColumnDataDataSchema } from "./aitm.schema.ts";
import { updateColumnData, UpdateColumnDataData } from "..";

export default tool({
  description: `
  Update column data
Set the content of a custom column
    `,
  parameters: updateColumnDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateColumnDataData, "url"> ) => {
    try {
      const { data } = await updateColumnData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    