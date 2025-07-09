
import { tool } from "ai";
import { deleteUserFromRootAccountDataSchema } from "./aitm.schema.ts";
import { deleteUserFromRootAccount, DeleteUserFromRootAccountData } from "..";

export default tool({
  description: `
  Delete a user from the root account
Delete a user record from a Canvas root account. If a user is
associated
with multiple root accounts (in a multi-tenant instance of Canvas), this
action will NOT
remove them from the other accounts.

WARNING: This API will allow a user to remove themselves from
the account.
If they do this, they won't be able to make API calls or log into Canvas at
that
account.
    `,
  parameters: deleteUserFromRootAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteUserFromRootAccountData, "url"> ) => {
    try {
      const { data } = await deleteUserFromRootAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    