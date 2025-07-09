
import { tool } from "ai";
import { editUserDataSchema } from "./aitm.schema.ts";
import { editUser, EditUserData } from "..";

export default tool({
  description: `
  Edit a user
Modify an existing user. To modify a user's login, see the documentation for logins.
    `,
  parameters: editUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditUserData, "url"> ) => {
    try {
      const { data } = await editUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    