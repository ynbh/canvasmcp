
import { tool } from "ai";
import { listAvailableReportsDataSchema } from "./aitm.schema.ts";
import { listAvailableReports, ListAvailableReportsData } from "..";

export default tool({
  description: `
  List Available Reports
Returns a paginated list of reports for the current context.
    `,
  parameters: listAvailableReportsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAvailableReportsData, "url"> ) => {
    try {
      const { data } = await listAvailableReports(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    