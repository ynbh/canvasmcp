
import { tool } from "ai";
import { deleteUserLoginDataSchema } from "./aitm.schema.ts";
import { deleteUserLogin, DeleteUserLoginData } from "..";

export default tool({
  description: `
  Delete a user login
Delete an existing login.
    `,
  parameters: deleteUserLoginDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteUserLoginData, "url"> ) => {
    try {
      const { data } = await deleteUserLogin(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    