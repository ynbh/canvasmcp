
import { tool } from "ai";
import { createUserLoginDataSchema } from "./aitm.schema.ts";
import { createUserLogin, CreateUserLoginData } from "..";

export default tool({
  description: `
  Create a user login
Create a new login for an existing user in the given account.
    `,
  parameters: createUserLoginDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateUserLoginData, "url"> ) => {
    try {
      const { data } = await createUserLogin(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    