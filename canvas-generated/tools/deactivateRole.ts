
import { tool } from "ai";
import { deactivateRoleDataSchema } from "./aitm.schema.ts";
import { deactivateRole, DeactivateRoleData } from "..";

export default tool({
  description: `
  Deactivate a role
Deactivates a custom role.  This hides it in the user interface and prevents
it
from being assigned to new users.  Existing users assigned to the role will
continue to function
with the same permissions they had previously.
Built-in roles cannot be deactivated.
    `,
  parameters: deactivateRoleDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeactivateRoleData, "url"> ) => {
    try {
      const { data } = await deactivateRole(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    