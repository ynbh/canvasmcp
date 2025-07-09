
import { tool } from "ai";
import { createCustomGradebookColumnDataSchema } from "./aitm.schema.ts";
import { createCustomGradebookColumn, CreateCustomGradebookColumnData } from "..";

export default tool({
  description: `
  Create a custom gradebook column
Create a custom gradebook column
    `,
  parameters: createCustomGradebookColumnDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateCustomGradebookColumnData, "url"> ) => {
    try {
      const { data } = await createCustomGradebookColumn(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    