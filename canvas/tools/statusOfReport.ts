
import { tool } from "ai";
import { statusOfReportDataSchema } from "./aitm.schema.ts";
import { statusOfReport, StatusOfReportData } from "..";

export default tool({
  description: `
  Status of a Report
Returns the status of a report.
    `,
  parameters: statusOfReportDataSchema.omit({ url: true }),
  execute: async (args : Omit<StatusOfReportData, "url"> ) => {
    try {
      const { data } = await statusOfReport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    