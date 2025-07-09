
import { tool } from "ai";
import { showOriginalityReportFilesDataSchema } from "./aitm.schema.ts";
import { showOriginalityReportFiles, ShowOriginalityReportFilesData } from "..";

export default tool({
  description: `
  Show an Originality Report
Get a single originality report
    `,
  parameters: showOriginalityReportFilesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowOriginalityReportFilesData, "url"> ) => {
    try {
      const { data } = await showOriginalityReportFiles(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    