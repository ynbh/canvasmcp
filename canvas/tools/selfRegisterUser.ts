
import { tool } from "ai";
import { selfRegisterUserDataSchema } from "./aitm.schema.ts";
import { selfRegisterUser, SelfRegisterUserData } from "..";

export default tool({
  description: `
  Self register a user
Self register and return a new user and pseudonym for an account.

If
self-registration is enabled on the account, you can use this
endpoint to self register new users.
    `,
  parameters: selfRegisterUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<SelfRegisterUserData, "url"> ) => {
    try {
      const { data } = await selfRegisterUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    