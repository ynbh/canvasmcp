
import { tool } from "ai";
import { updateRoleDataSchema } from "./aitm.schema.ts";
import { updateRole, UpdateRoleData } from "..";

export default tool({
  description: `
  Update a role
Update permissions for an existing role.

Recognized roles are:
* TeacherEnrollment
*
StudentEnrollment
* TaEnrollment
* ObserverEnrollment
* DesignerEnrollment
* AccountAdmin
* Any
previously created custom role
    `,
  parameters: updateRoleDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateRoleData, "url"> ) => {
    try {
      const { data } = await updateRole(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    