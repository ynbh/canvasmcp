
import { tool } from "ai";
import { updateCustomGradebookColumnDataSchema } from "./aitm.schema.ts";
import { updateCustomGradebookColumn, UpdateCustomGradebookColumnData } from "..";

export default tool({
  description: `
  Update a custom gradebook column
Accepts the same parameters as custom gradebook column creation
    `,
  parameters: updateCustomGradebookColumnDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCustomGradebookColumnData, "url"> ) => {
    try {
      const { data } = await updateCustomGradebookColumn(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    