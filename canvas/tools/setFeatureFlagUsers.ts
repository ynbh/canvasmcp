
import { tool } from "ai";
import { setFeatureFlagUsersDataSchema } from "./aitm.schema.ts";
import { setFeatureFlagUsers, SetFeatureFlagUsersData } from "..";

export default tool({
  description: `
  Set feature flag
Set a feature flag for a given Account, Course, or User. This call will fail if a
parent account sets
a feature flag for the same feature in any state other than "allowed".
    `,
  parameters: setFeatureFlagUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetFeatureFlagUsersData, "url"> ) => {
    try {
      const { data } = await setFeatureFlagUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    