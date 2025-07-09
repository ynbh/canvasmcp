
import { tool } from "ai";
import { editUserLoginDataSchema } from "./aitm.schema.ts";
import { editUserLogin, EditUserLoginData } from "..";

export default tool({
  description: `
  Edit a user login
Update an existing login for a user in the given account.
    `,
  parameters: editUserLoginDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditUserLoginData, "url"> ) => {
    try {
      const { data } = await editUserLogin(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    