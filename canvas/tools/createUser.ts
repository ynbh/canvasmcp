
import { tool } from "ai";
import { createUserDataSchema } from "./aitm.schema.ts";
import { createUser, CreateUserData } from "..";

export default tool({
  description: `
  Create a user
Create and return a new user and pseudonym for an account.

If you don't have the
"Modify login details for users" permission, but
self-registration is enabled on the account, you
can still use this
endpoint to register new users. Certain fields will be required, and
others will
be ignored (see below).
    `,
  parameters: createUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateUserData, "url"> ) => {
    try {
      const { data } = await createUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    