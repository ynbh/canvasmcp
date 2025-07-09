
import { tool } from "ai";
import { coursePermissionDataSchema } from "./aitm.schema.ts";
import { coursePermission, CoursePermissionData } from "..";

export default tool({
  description: `
  Permissions
Returns permission information for the calling user in the given course.
See also the
{api:AccountsController#permissions Account} and
{api:GroupsController#permissions Group}
counterparts.
    `,
  parameters: coursePermissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CoursePermissionData, "url"> ) => {
    try {
      const { data } = await coursePermission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    