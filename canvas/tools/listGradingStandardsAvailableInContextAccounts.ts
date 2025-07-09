
import { tool } from "ai";
import { listGradingStandardsAvailableInContextAccountsDataSchema } from "./aitm.schema.ts";
import { listGradingStandardsAvailableInContextAccounts, ListGradingStandardsAvailableInContextAccountsData } from "..";

export default tool({
  description: `
  List the grading standards available in a context.
Returns the paginated list of grading standards
for the given context that are visible to the user.
    `,
  parameters: listGradingStandardsAvailableInContextAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGradingStandardsAvailableInContextAccountsData, "url"> ) => {
    try {
      const { data } = await listGradingStandardsAvailableInContextAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    