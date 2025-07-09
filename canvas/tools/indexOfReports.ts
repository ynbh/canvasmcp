
import { tool } from "ai";
import { indexOfReportsDataSchema } from "./aitm.schema.ts";
import { indexOfReports, IndexOfReportsData } from "..";

export default tool({
  description: `
  Index of Reports
Shows all reports that have been run for the account of a specific type.
    `,
  parameters: indexOfReportsDataSchema.omit({ url: true }),
  execute: async (args : Omit<IndexOfReportsData, "url"> ) => {
    try {
      const { data } = await indexOfReports(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    