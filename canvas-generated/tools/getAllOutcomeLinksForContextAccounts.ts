
import { tool } from "ai";
import { getAllOutcomeLinksForContextAccountsDataSchema } from "./aitm.schema.ts";
import { getAllOutcomeLinksForContextAccounts, GetAllOutcomeLinksForContextAccountsData } from "..";

export default tool({
  description: `
  Get all outcome links for context
    `,
  parameters: getAllOutcomeLinksForContextAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllOutcomeLinksForContextAccountsData, "url"> ) => {
    try {
      const { data } = await getAllOutcomeLinksForContextAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    