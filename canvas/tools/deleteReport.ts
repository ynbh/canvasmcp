
import { tool } from "ai";
import { deleteReportDataSchema } from "./aitm.schema.ts";
import { deleteReport, DeleteReportData } from "..";

export default tool({
  description: `
  Delete a Report
Deletes a generated report instance.
    `,
  parameters: deleteReportDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteReportData, "url"> ) => {
    try {
      const { data } = await deleteReport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    