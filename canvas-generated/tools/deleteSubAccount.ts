
import { tool } from "ai";
import { deleteSubAccountDataSchema } from "./aitm.schema.ts";
import { deleteSubAccount, DeleteSubAccountData } from "..";

export default tool({
  description: `
  Delete a sub-account
Cannot delete an account with active courses or active sub_accounts.
Cannot
delete a root_account
    `,
  parameters: deleteSubAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteSubAccountData, "url"> ) => {
    try {
      const { data } = await deleteSubAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    