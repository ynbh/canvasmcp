
import { tool } from "ai";
import { listCustomGradebookColumnsDataSchema } from "./aitm.schema.ts";
import { listCustomGradebookColumns, ListCustomGradebookColumnsData } from "..";

export default tool({
  description: `
  List custom gradebook columns
A paginated list of all custom gradebook columns for a course
    `,
  parameters: listCustomGradebookColumnsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCustomGradebookColumnsData, "url"> ) => {
    try {
      const { data } = await listCustomGradebookColumns(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    