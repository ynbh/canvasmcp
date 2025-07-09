
import { tool } from "ai";
import { groupPermissionDataSchema } from "./aitm.schema.ts";
import { groupPermission, GroupPermissionData } from "..";

export default tool({
  description: `
  Permissions
Returns permission information for the calling user in the given group.
See also the
{api:AccountsController#permissions Account} and
{api:CoursesController#permissions Course}
counterparts.
    `,
  parameters: groupPermissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GroupPermissionData, "url"> ) => {
    try {
      const { data } = await groupPermission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    