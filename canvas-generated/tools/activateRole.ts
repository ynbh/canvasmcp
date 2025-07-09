
import { tool } from "ai";
import { activateRoleDataSchema } from "./aitm.schema.ts";
import { activateRole, ActivateRoleData } from "..";

export default tool({
  description: `
  Activate a role
Re-activates an inactive role (allowing it to be assigned to new users)
    `,
  parameters: activateRoleDataSchema.omit({ url: true }),
  execute: async (args : Omit<ActivateRoleData, "url"> ) => {
    try {
      const { data } = await activateRole(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    