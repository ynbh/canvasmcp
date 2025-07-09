
import { tool } from "ai";
import { createNewSubAccountDataSchema } from "./aitm.schema.ts";
import { createNewSubAccount, CreateNewSubAccountData } from "..";

export default tool({
  description: `
  Create a new sub-account
Add a new sub-account to a given account.
    `,
  parameters: createNewSubAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateNewSubAccountData, "url"> ) => {
    try {
      const { data } = await createNewSubAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    