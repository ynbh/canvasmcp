
import { tool } from "ai";
import { showUserDetailsDataSchema } from "./aitm.schema.ts";
import { showUserDetails, ShowUserDetailsData } from "..";

export default tool({
  description: `
  Show user details
Shows details for user.

Also includes an attribute "permissions", a
non-comprehensive list of permissions for the user.
Example:
!!!javascript
"permissions":
{
"can_update_name": true, // Whether the user can update their name.
"can_update_avatar": false //
Whether the user can update their avatar.
}
    `,
  parameters: showUserDetailsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowUserDetailsData, "url"> ) => {
    try {
      const { data } = await showUserDetails(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    