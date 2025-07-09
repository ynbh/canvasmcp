
import { tool } from "ai";
import { getQuizReportDataSchema } from "./aitm.schema.ts";
import { getQuizReport, GetQuizReportData } from "..";

export default tool({
  description: `
  Get a quiz report
Returns the data for a single quiz report.
    `,
  parameters: getQuizReportDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetQuizReportData, "url"> ) => {
    try {
      const { data } = await getQuizReport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    