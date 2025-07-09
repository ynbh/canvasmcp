
import { tool } from "ai";
import { getSingleAccountDataSchema } from "./aitm.schema.ts";
import { getSingleAccount, GetSingleAccountData } from "..";

export default tool({
  description: `
  Get a single account
Retrieve information on an individual account, given by id or
sis
sis_account_id.
    `,
  parameters: getSingleAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleAccountData, "url"> ) => {
    try {
      const { data } = await getSingleAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    