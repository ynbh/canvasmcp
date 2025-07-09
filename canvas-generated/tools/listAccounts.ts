
import { tool } from "ai";
import { listAccountsDataSchema } from "./aitm.schema.ts";
import { listAccounts, ListAccountsData } from "..";

export default tool({
  description: `
  List accounts
A paginated list of accounts that the current user can view or manage.
Typically,
students and even teachers will get an empty list in response,
only account admins can view the
accounts that they are in.
    `,
  parameters: listAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAccountsData, "url"> ) => {
    try {
      const { data } = await listAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    