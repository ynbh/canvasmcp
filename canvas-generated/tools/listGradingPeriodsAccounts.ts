
import { tool } from "ai";
import { listGradingPeriodsAccountsDataSchema } from "./aitm.schema.ts";
import { listGradingPeriodsAccounts, ListGradingPeriodsAccountsData } from "..";

export default tool({
  description: `
  List grading periods
Returns the paginated list of grading periods for the current course.
    `,
  parameters: listGradingPeriodsAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGradingPeriodsAccountsData, "url"> ) => {
    try {
      const { data } = await listGradingPeriodsAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    