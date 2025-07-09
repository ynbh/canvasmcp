
import { tool } from "ai";
import { makeAccountAdminDataSchema } from "./aitm.schema.ts";
import { makeAccountAdmin, MakeAccountAdminData } from "..";

export default tool({
  description: `
  Make an account admin
Flag an existing user as an admin within the account.
    `,
  parameters: makeAccountAdminDataSchema.omit({ url: true }),
  execute: async (args : Omit<MakeAccountAdminData, "url"> ) => {
    try {
      const { data } = await makeAccountAdmin(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    