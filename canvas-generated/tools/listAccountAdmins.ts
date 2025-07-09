
import { tool } from "ai";
import { listAccountAdminsDataSchema } from "./aitm.schema.ts";
import { listAccountAdmins, ListAccountAdminsData } from "..";

export default tool({
  description: `
  List account admins
A paginated list of the admins in the account
    `,
  parameters: listAccountAdminsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAccountAdminsData, "url"> ) => {
    try {
      const { data } = await listAccountAdmins(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    