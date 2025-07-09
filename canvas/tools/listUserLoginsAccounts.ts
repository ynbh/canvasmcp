
import { tool } from "ai";
import { listUserLoginsAccountsDataSchema } from "./aitm.schema.ts";
import { listUserLoginsAccounts, ListUserLoginsAccountsData } from "..";

export default tool({
  description: `
  List user logins
Given a user ID, return a paginated list of that user's logins for the given
account.
    `,
  parameters: listUserLoginsAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUserLoginsAccountsData, "url"> ) => {
    try {
      const { data } = await listUserLoginsAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    