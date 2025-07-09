
import { tool } from "ai";
import { editOriginalityReportSubmissionsDataSchema } from "./aitm.schema.ts";
import { editOriginalityReportSubmissions, EditOriginalityReportSubmissionsData } from "..";

export default tool({
  description: `
  Edit an Originality Report
Modify an existing originality report. An alternative to this endpoint
is
to POST the same parameters listed below to the CREATE endpoint.
    `,
  parameters: editOriginalityReportSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditOriginalityReportSubmissionsData, "url"> ) => {
    try {
      const { data } = await editOriginalityReportSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    