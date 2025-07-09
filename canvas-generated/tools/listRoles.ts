
import { tool } from "ai";
import { listRolesDataSchema } from "./aitm.schema.ts";
import { listRoles, ListRolesData } from "..";

export default tool({
  description: `
  List roles
A paginated list of the roles available to an account.
    `,
  parameters: listRolesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListRolesData, "url"> ) => {
    try {
      const { data } = await listRoles(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    