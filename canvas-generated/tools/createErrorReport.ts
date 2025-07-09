
import { tool } from "ai";
import { createErrorReportDataSchema } from "./aitm.schema.ts";
import { createErrorReport, CreateErrorReportData } from "..";

export default tool({
  description: `
  Create Error Report
Create a new error report documenting an experienced problem

Performs the same
action as when a user uses the "help -> report a problem"
dialog.
    `,
  parameters: createErrorReportDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateErrorReportData, "url"> ) => {
    try {
      const { data } = await createErrorReport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    