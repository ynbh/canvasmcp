
import { tool } from "ai";
import { createOriginalityReportDataSchema } from "./aitm.schema.ts";
import { createOriginalityReport, CreateOriginalityReportData } from "..";

export default tool({
  description: `
  Create an Originality Report
Create a new OriginalityReport for the specified file
    `,
  parameters: createOriginalityReportDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateOriginalityReportData, "url"> ) => {
    try {
      const { data } = await createOriginalityReport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    