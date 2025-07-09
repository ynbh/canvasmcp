
import { tool } from "ai";
import { listGroupCategoriesForContextAccountsDataSchema } from "./aitm.schema.ts";
import { listGroupCategoriesForContextAccounts, ListGroupCategoriesForContextAccountsData } from "..";

export default tool({
  description: `
  List group categories for a context
Returns a paginated list of group categories in a context
    `,
  parameters: listGroupCategoriesForContextAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGroupCategoriesForContextAccountsData, "url"> ) => {
    try {
      const { data } = await listGroupCategoriesForContextAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    