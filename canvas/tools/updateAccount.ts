
import { tool } from "ai";
import { updateAccountDataSchema } from "./aitm.schema.ts";
import { updateAccount, UpdateAccountData } from "..";

export default tool({
  description: `
  Update an account
Update an existing account.
    `,
  parameters: updateAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateAccountData, "url"> ) => {
    try {
      const { data } = await updateAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    