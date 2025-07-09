
import { tool } from "ai";
import { createNewRoleDataSchema } from "./aitm.schema.ts";
import { createNewRole, CreateNewRoleData } from "..";

export default tool({
  description: `
  Create a new role
Create a new course-level or account-level role.
    `,
  parameters: createNewRoleDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateNewRoleData, "url"> ) => {
    try {
      const { data } = await createNewRole(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    