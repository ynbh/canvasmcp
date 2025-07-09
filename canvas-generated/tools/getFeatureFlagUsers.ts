
import { tool } from "ai";
import { getFeatureFlagUsersDataSchema } from "./aitm.schema.ts";
import { getFeatureFlagUsers, GetFeatureFlagUsersData } from "..";

export default tool({
  description: `
  Get feature flag
Get the feature flag that applies to a given Account, Course, or User.
The flag may
be defined on the object, or it may be inherited from a parent
account. You can look at the
context_id and context_type of the returned object
to determine which is the case. If these fields
are missing, then the object
is the global Canvas default.
    `,
  parameters: getFeatureFlagUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetFeatureFlagUsersData, "url"> ) => {
    try {
      const { data } = await getFeatureFlagUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    