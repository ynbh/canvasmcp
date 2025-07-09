
import { tool } from "ai";
import { redirectToRootOutcomeGroupForContextAccountsDataSchema } from "./aitm.schema.ts";
import { redirectToRootOutcomeGroupForContextAccounts, RedirectToRootOutcomeGroupForContextAccountsData } from "..";

export default tool({
  description: `
  Redirect to root outcome group for context
Convenience redirect to find the root outcome group for a
particular
context. Will redirect to the appropriate outcome group's URL.
    `,
  parameters: redirectToRootOutcomeGroupForContextAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RedirectToRootOutcomeGroupForContextAccountsData, "url"> ) => {
    try {
      const { data } = await redirectToRootOutcomeGroupForContextAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    