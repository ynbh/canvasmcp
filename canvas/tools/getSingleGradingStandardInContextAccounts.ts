
import { tool } from "ai";
import { getSingleGradingStandardInContextAccountsDataSchema } from "./aitm.schema.ts";
import { getSingleGradingStandardInContextAccounts, GetSingleGradingStandardInContextAccountsData } from "..";

export default tool({
  description: `
  Get a single grading standard in a context.
Returns a grading standard for the given context that is
visible to the user.
    `,
  parameters: getSingleGradingStandardInContextAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleGradingStandardInContextAccountsData, "url"> ) => {
    try {
      const { data } = await getSingleGradingStandardInContextAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    