
import { tool } from "ai";
import { createQuizReportDataSchema } from "./aitm.schema.ts";
import { createQuizReport, CreateQuizReportData } from "..";

export default tool({
  description: `
  Create a quiz report
Create and return a new report for this quiz. If a previously
generated report
matches the arguments and is still current (i.e.
there have been no new submissions), it will be
returned.

*Responses*

* <code>400 Bad Request</code> if the specified report type is invalid
*
<code>409 Conflict</code> if a quiz report of the specified type is already being
generated
    `,
  parameters: createQuizReportDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateQuizReportData, "url"> ) => {
    try {
      const { data } = await createQuizReport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    