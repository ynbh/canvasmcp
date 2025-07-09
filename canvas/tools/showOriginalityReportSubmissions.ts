
import { tool } from "ai";
import { showOriginalityReportSubmissionsDataSchema } from "./aitm.schema.ts";
import { showOriginalityReportSubmissions, ShowOriginalityReportSubmissionsData } from "..";

export default tool({
  description: `
  Show an Originality Report
Get a single originality report
    `,
  parameters: showOriginalityReportSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowOriginalityReportSubmissionsData, "url"> ) => {
    try {
      const { data } = await showOriginalityReportSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    