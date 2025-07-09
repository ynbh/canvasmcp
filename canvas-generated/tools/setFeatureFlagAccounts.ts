
import { tool } from "ai";
import { setFeatureFlagAccountsDataSchema } from "./aitm.schema.ts";
import { setFeatureFlagAccounts, SetFeatureFlagAccountsData } from "..";

export default tool({
  description: `
  Set feature flag
Set a feature flag for a given Account, Course, or User. This call will fail if a
parent account sets
a feature flag for the same feature in any state other than "allowed".
    `,
  parameters: setFeatureFlagAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetFeatureFlagAccountsData, "url"> ) => {
    try {
      const { data } = await setFeatureFlagAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    