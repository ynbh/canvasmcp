
import { tool } from "ai";
import { editOriginalityReportFilesDataSchema } from "./aitm.schema.ts";
import { editOriginalityReportFiles, EditOriginalityReportFilesData } from "..";

export default tool({
  description: `
  Edit an Originality Report
Modify an existing originality report. An alternative to this endpoint
is
to POST the same parameters listed below to the CREATE endpoint.
    `,
  parameters: editOriginalityReportFilesDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditOriginalityReportFilesData, "url"> ) => {
    try {
      const { data } = await editOriginalityReportFiles(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    