
import { tool } from "ai";
import { deleteCustomGradebookColumnDataSchema } from "./aitm.schema.ts";
import { deleteCustomGradebookColumn, DeleteCustomGradebookColumnData } from "..";

export default tool({
  description: `
  Delete a custom gradebook column
Permanently deletes a custom column and its associated data
    `,
  parameters: deleteCustomGradebookColumnDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteCustomGradebookColumnData, "url"> ) => {
    try {
      const { data } = await deleteCustomGradebookColumn(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    