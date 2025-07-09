
import { tool } from "ai";
import { getSubAccountsOfAccountDataSchema } from "./aitm.schema.ts";
import { getSubAccountsOfAccount, GetSubAccountsOfAccountData } from "..";

export default tool({
  description: `
  Get the sub-accounts of an account
List accounts that are sub-accounts of the given account.
    `,
  parameters: getSubAccountsOfAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSubAccountsOfAccountData, "url"> ) => {
    try {
      const { data } = await getSubAccountsOfAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    