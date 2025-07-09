
import { tool } from "ai";
import { removeAccountAdminDataSchema } from "./aitm.schema.ts";
import { removeAccountAdmin, RemoveAccountAdminData } from "..";

export default tool({
  description: `
  Remove account admin
Remove the rights associated with an account admin role from a user.
    `,
  parameters: removeAccountAdminDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveAccountAdminData, "url"> ) => {
    try {
      const { data } = await removeAccountAdmin(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    