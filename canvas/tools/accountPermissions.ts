
import { tool } from "ai";
import { accountPermissionsDataSchema } from "./aitm.schema.ts";
import { accountPermissions, AccountPermissionsData } from "..";

export default tool({
  description: `
  Permissions
Returns permission information for the calling user and the given account.
You may use
`self` as the account id to check permissions against the domain root account.
The caller must have
an account role or admin (teacher/TA/designer) enrollment in a course
in the account.

See also the
{api:CoursesController#permissions Course} and {api:GroupsController#permissions
Group}
counterparts.
    `,
  parameters: accountPermissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<AccountPermissionsData, "url"> ) => {
    try {
      const { data } = await accountPermissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    