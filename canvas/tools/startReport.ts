
import { tool } from "ai";
import { startReportDataSchema } from "./aitm.schema.ts";
import { startReport, StartReportData } from "..";

export default tool({
  description: `
  Start a Report
Generates a report instance for the account. Note that "report" in the
request must
match one of the available report names. To fetch a list of
available report names and parameters
for each report (including whether or
not those parameters are required),
see
{api:AccountReportsController#available_reports List Available Reports}.
    `,
  parameters: startReportDataSchema.omit({ url: true }),
  execute: async (args : Omit<StartReportData, "url"> ) => {
    try {
      const { data } = await startReport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    