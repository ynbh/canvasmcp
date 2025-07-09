
import { tool } from "ai";
import { listGroupsAvailableInContextAccountsDataSchema } from "./aitm.schema.ts";
import { listGroupsAvailableInContextAccounts, ListGroupsAvailableInContextAccountsData } from "..";

export default tool({
  description: `
  List the groups available in a context.
Returns the paginated list of active groups in the given
context that are visible to user.
    `,
  parameters: listGroupsAvailableInContextAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGroupsAvailableInContextAccountsData, "url"> ) => {
    try {
      const { data } = await listGroupsAvailableInContextAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    