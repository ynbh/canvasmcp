
import { tool } from "ai";
import { removeFeatureFlagAccountsDataSchema } from "./aitm.schema.ts";
import { removeFeatureFlagAccounts, RemoveFeatureFlagAccountsData } from "..";

export default tool({
  description: `
  Remove feature flag
Remove feature flag for a given Account, Course, or User.  (Note that the flag
must
be defined on the Account, Course, or User directly.)  The object will then inherit
the feature
flags from a higher account, if any exist.  If this flag was 'on' or 'off',
then lower-level account
flags that were masked by this one will apply again.
    `,
  parameters: removeFeatureFlagAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveFeatureFlagAccountsData, "url"> ) => {
    try {
      const { data } = await removeFeatureFlagAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    