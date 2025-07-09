
import { tool } from "ai";
import { getSingleRoleDataSchema } from "./aitm.schema.ts";
import { getSingleRole, GetSingleRoleData } from "..";

export default tool({
  description: `
  Get a single role
Retrieve information about a single role
    `,
  parameters: getSingleRoleDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleRoleData, "url"> ) => {
    try {
      const { data } = await getSingleRole(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    